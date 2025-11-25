from datetime import datetime, timedelta, UTC
from collections import defaultdict
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from scripts.extensions import db, get_setting
from scripts.models import User, Submission, Challenge, Award, FlagAttempt, Category, UserHint, Hint
import math
from scripts.cache import cached
from flask import current_app

def _calculate_stats(data):
    if not data:
        return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'q1': 0, 'q3': 0}
    
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = math.sqrt(variance)
    
    sorted_data = sorted(data)
    
    q1_index = (n - 1) * 0.25
    q3_index = (n - 1) * 0.75
    
    q1 = sorted_data[int(q1_index)]
    q3 = sorted_data[int(q3_index)]
    
    return {
        'mean': mean,
        'std': std_dev,
        'min': min(data),
        'max': max(data),
        'q1': q1,
        'q3': q3
    }

def get_global_score_history_data():
    """
    Generates time series data for global score statistics (min, max, avg, std dev, Q1, Q3)
    across all active users, and individual user cumulative scores over time.

    Returns:
        dict: A dictionary containing:
            - 'global_stats_over_time': List of dicts, each with 'x' (timestamp) and global stats.
            - 'user_scores_over_time': Dict where keys are usernames and values are lists of dicts
                                       (timestamp, cumulative score for that user).
    """
    if current_app.config['ENABLE_REDIS_CACHE'] and current_app.redis:
        @cached(key_prefix='global_score_history', timeout=60)
        def _get_global_score_history_data_cached():
            return _get_global_score_history_data_uncached()
        return _get_global_score_history_data_cached()
    else:
        return _get_global_score_history_data_uncached()


    # Fetch all relevant events (submissions and awards) ordered by timestamp
    all_events = []

    # Get all submissions
    submissions = Submission.query.options(
        joinedload(Submission.challenge_rel)
    ).order_by(Submission.timestamp.asc()).all()
    for sub in submissions:
        all_events.append({
            'type': 'submission',
            'timestamp': sub.timestamp,
            'user_id': sub.user_id,
            'points': sub.challenge_rel.points
        })

    # Get all awards
    awards = Award.query.order_by(Award.timestamp.asc()).all()
    for award in awards:
        all_events.append({
            'type': 'award',
            'timestamp': award.timestamp,
            'user_id': award.user_id,
            'points': award.points_awarded
        })

    # Sort all events by timestamp
    all_events.sort(key=lambda x: x['timestamp'])

    # Initialize user scores and history
    all_users = User.query.all() # Get all users, regardless of hidden status
    user_current_scores = {user.id: 0 for user in all_users}
    user_scores_history = defaultdict(list) # {user_id: [{'x': timestamp, 'y': score}, ...]}

    # Initialize global stats history
    global_stats_over_time = []

    # Add an initial point for all users at time 0
    if all_events:
        earliest_event_timestamp = all_events[0]['timestamp']
        initial_timestamp = earliest_event_timestamp - timedelta(days=1)
    else:
        initial_timestamp = datetime.now(UTC)
    
    # Populate initial user scores history
    for user in all_users:
        user_scores_history[user.username].append({'x': initial_timestamp.isoformat(), 'y': 0})

    # Calculate initial global stats
    if all_users:
        global_stats_over_time.append({
            'x': initial_timestamp.isoformat(),
            'min': 0, 'max': 0, 'avg': 0, 'std_dev': 0, 'q1': 0, 'q3': 0
        })
    else:
        global_stats_over_time.append({
            'x': initial_timestamp.isoformat(),
            'min': 0, 'max': 0, 'avg': 0, 'std_dev': 0, 'q1': 0, 'q3': 0
        })

    # Create a mapping from user_id to username for quick lookup
    user_id_to_username = {user.id: user.username for user in all_users}

    # Process events chronologically and store daily snapshots of user scores
    daily_user_scores_snapshots = defaultdict(lambda: {user.id: 0 for user in all_users})
    latest_timestamp = initial_timestamp

    for event in all_events:
        user_id = event['user_id']
        points_change = event['points']
        timestamp = event['timestamp']

        # Update the user's current score
        user_current_scores[user_id] += points_change

        # Record the current score for the specific user
        username = user_id_to_username.get(user_id)
        if username:
            user_scores_history[username].append({'x': timestamp.isoformat(), 'y': user_current_scores[user_id]})
        
        # Update the daily snapshot for the current day
        day_key = timestamp.date()
        daily_user_scores_snapshots[day_key] = user_current_scores.copy() # Store a copy of current scores
        latest_timestamp = max(latest_timestamp, timestamp)

    # Generate global statistics for each day
    global_stats_over_time = []
    current_day = initial_timestamp.date()
    
    # Ensure initial point is added if there are users
    if all_users:
        global_stats_over_time.append({
            'x': initial_timestamp.isoformat(),
            'min': 0, 'max': 0, 'avg': 0, 'std_dev': 0, 'q1': 0, 'q3': 0
        })

    while current_day <= latest_timestamp.date():
        snapshot_scores = daily_user_scores_snapshots.get(current_day)
        
        # If no events on this specific day, use the last known snapshot
        if not snapshot_scores and global_stats_over_time:
            # Use the previous day's scores if available, otherwise keep current_user_scores
            # This ensures continuity for days without events
            previous_day_scores = global_stats_over_time[-1]
            global_stats_over_time.append({
                'x': datetime.combine(current_day, datetime.min.time(), tzinfo=UTC).isoformat(),
                'min': previous_day_scores['min'],
                'max': previous_day_scores['max'],
                'avg': previous_day_scores['avg'],
                'std_dev': previous_day_scores['std_dev'],
                'q1': previous_day_scores['q1'],
                'q3': previous_day_scores['q3']
            })
        elif snapshot_scores:
            eligible_scores = []
            for user in all_users:
                if not user.hidden and snapshot_scores[user.id] > 0: # Exclude hidden users and users with 0 score
                    eligible_scores.append(snapshot_scores[user.id])
            
            if eligible_scores:
                stats = _calculate_stats(eligible_scores)
                global_stats_over_time.append({
                    'x': datetime.combine(current_day, datetime.min.time(), tzinfo=UTC).isoformat(),
                    'min': stats['min'],
                    'max': stats['max'],
                    'avg': stats['mean'],
                    'std_dev': stats['std'],
                    'q1': stats['q1'],
                    'q3': stats['q3']
                })
            else:
                # If no eligible scores after filtering, append zeros
                global_stats_over_time.append({
                    'x': datetime.combine(current_day, datetime.min.time(), tzinfo=UTC).isoformat(),
                    'min': 0, 'max': 0, 'avg': 0, 'std_dev': 0, 'q1': 0, 'q3': 0
                })
        current_day += timedelta(days=1)
    
    # Ensure all users have the same number of points in their history for consistent charting
    # Fill in gaps for users who didn't have an event at every global timestamp
    all_global_timestamps = sorted(list(set([d['x'] for d in global_stats_over_time])))

    final_user_scores_history = {}
    for user in all_users: # Iterate through all_users to ensure all are included
        username = user.username
        history = user_scores_history.get(username, [])
        final_user_scores_history[username] = []
        current_score = 0
        history_idx = 0
        for global_ts in all_global_timestamps:
            # Find the latest score for this user up to or at the current global timestamp
            while history_idx < len(history) and history[history_idx]['x'] <= global_ts:
                current_score = history[history_idx]['y']
                history_idx += 1
            final_user_scores_history[username].append({'x': global_ts, 'y': current_score})

    return {
        'global_stats_over_time': global_stats_over_time,
        'user_scores_over_time': final_user_scores_history
    }

def get_profile_points_over_time_data(target_user, db_session, get_setting_func, Submission_model, Challenge_model, Category_model, User_model, UTC_tz, timedelta_obj):
    """
    Generates data for the 'Points Over Time Chart' and associated statistics for a given user.

    Args:
        target_user (User): The user object for whom to generate the data.
        db_session: The SQLAlchemy session object.
        get_setting_func (function): Function to retrieve application settings.
        Submission_model: The Submission model.
        Challenge_model: The Challenge model.
        Category_model: The Category model.
        User_model: The User model.
        UTC_tz: The UTC timezone object.
        timedelta_obj: The timedelta object.

    Returns:
        tuple: A tuple containing:
            - dict: profile_charts_data for points over time and global stats.
            - dict: profile_stats_data for overall score statistics.
    """
    profile_charts_data = {}
    profile_stats_data = {}

    if get_setting_func('PROFILE_POINTS_OVER_TIME_CHART_ENABLED', 'True').lower() == 'true':
        points_over_time_data = []
        cumulative_score = 0
        all_scores = []
        
        submissions_for_chart = db_session.query(Submission_model).filter_by(user_id=target_user.id)\
                                                .options(joinedload(Submission_model.challenge_rel).joinedload(Challenge_model.category))\
                                                .order_by(Submission_model.timestamp.asc())\
                                                .all()
        
        if submissions_for_chart:
            initial_timestamp = submissions_for_chart[0].timestamp - timedelta_obj(microseconds=1)
            points_over_time_data.append({'x': initial_timestamp.isoformat(), 'y': 0, 'category': 'Start'})

            for submission in submissions_for_chart:
                cumulative_score += submission.challenge_rel.points
                all_scores.append(cumulative_score)
                points_over_time_data.append({
                    'x': submission.timestamp.isoformat(),
                    'y': cumulative_score,
                    'category': submission.challenge_rel.category.name if submission.challenge_rel.category else 'Uncategorized'
                })
        else:
            points_over_time_data.append({'x': datetime.now(UTC_tz).isoformat(), 'y': 0, 'category': 'Start'})
        
        profile_charts_data['points_over_time'] = points_over_time_data

        global_chart_data = get_global_score_history_data()
        
        profile_charts_data['global_stats_over_time'] = global_chart_data['global_stats_over_time']
        
        target_user_history = global_chart_data['user_scores_over_time'].get(target_user.username, [])
        if not target_user_history or target_user_history[0]['y'] != 0:
            target_user_history.insert(0, {'x': datetime.min.replace(tzinfo=UTC_tz).isoformat(), 'y': 0})
        profile_charts_data['target_user_score_history'] = target_user_history

        if all_scores:
            # Calculate overall statistics from all eligible users
            eligible_users = db_session.query(User_model)\
                                       .filter(User_model.hidden == False)\
                                       .join(Submission_model, User_model.id == Submission_model.user_id)\
                                       .group_by(User_model.id)\
                                       .having(func.count(Submission_model.id) > 0)\
                                       .all()
            
            overall_scores_list = []
            for user in eligible_users:
                if user.score > 0:
                    overall_scores_list.append(user.score)

            if overall_scores_list:
                stats = _calculate_stats(overall_scores_list)
                profile_stats_data['max_score'] = stats['max']
                profile_stats_data['min_score'] = stats['min']
                profile_stats_data['average_score'] = stats['mean']
                profile_stats_data['std_dev'] = stats['std']
                profile_stats_data['iqr'] = stats['q3'] - stats['q1']
            else:
                profile_stats_data['max_score'] = 0.0
                profile_stats_data['min_score'] = 0.0
                profile_stats_data['average_score'] = 0.0
                profile_stats_data['std_dev'] = 0.0
                profile_stats_data['iqr'] = 0.0
        else:
            profile_stats_data['max_score'] = 0.0
            profile_stats_data['min_score'] = 0.0
            profile_stats_data['average_score'] = 0.0
            profile_stats_data['std_dev'] = 0.0
            profile_stats_data['iqr'] = 0.0
        
        # Initialize these even if no scores, to prevent KeyError in template
        profile_charts_data['moving_average'] = []
        profile_charts_data['plus_one_std_dev'] = []
        profile_charts_data['minus_one_std_dev'] = []
        profile_charts_data['moving_max'] = []
        profile_charts_data['moving_min'] = []
        profile_charts_data['moving_q1'] = []
        profile_charts_data['moving_q3'] = []

    return profile_charts_data, profile_stats_data

def get_profile_fails_vs_succeeds_data(target_user, FlagAttempt_model, get_setting_func):
    """
    Generates data for the 'Fails vs. Succeeds Chart' for a given user.

    Args:
        target_user (User): The user object for whom to generate the data.
        FlagAttempt_model: The FlagAttempt model.
        get_setting_func (function): Function to retrieve application settings.

    Returns:
        dict: profile_charts_data containing fails vs. succeeds data.
    """
    profile_charts_data = {}
    if get_setting_func('PROFILE_FAILS_VS_SUCCEEDS_CHART_ENABLED', 'True').lower() == 'true':
        successful_attempts = FlagAttempt_model.query.filter_by(user_id=target_user.id, is_correct=True).count()
        failed_attempts = FlagAttempt_model.query.filter_by(user_id=target_user.id, is_correct=False).count()
        profile_charts_data['fails_vs_succeeds'] = {
            'labels': ['Succeeds', 'Fails'],
            'values': [successful_attempts, failed_attempts]
        }
    return profile_charts_data

def get_profile_categories_per_score_data(target_user, db_session, Category_model, Challenge_model, Submission_model, func_obj, get_setting_func):
    """
    Generates data for the 'Categories per Score Chart' for a given user.

    Args:
        target_user (User): The user object for whom to generate the data.
        db_session: The SQLAlchemy session object.
        Category_model: The Category model.
        Challenge_model: The Challenge model.
        Submission_model: The Submission model.
        func_obj: The SQLAlchemy func object.
        get_setting_func (function): Function to retrieve application settings.

    Returns:
        dict: profile_charts_data containing categories per score data.
    """
    profile_charts_data = {}
    if get_setting_func('PROFILE_CATEGORIES_PER_SCORE_CHART_ENABLED', 'True').lower() == 'true':
        category_scores = db_session.query(
            Category_model.name,
            func_obj.sum(Challenge_model.points)
        ).join(Challenge_model, Category_model.id == Challenge_model.category_id)\
         .join(Submission_model, Challenge_model.id == Submission_model.challenge_id)\
         .filter(Submission_model.user_id == target_user.id)\
         .group_by(Category_model.name)\
         .all()
        
        category_labels = [cs[0] for cs in category_scores]
        category_values = [cs[1] for cs in category_scores]
        profile_charts_data['categories_per_score'] = {
            'labels': category_labels,
            'values': category_values
        }
    return profile_charts_data

def get_profile_challenges_complete_data(target_user, Submission_model, UTC_tz, timedelta_obj, get_setting_func):
    """
    Generates data for the 'Challenges Complete Chart' (cumulative count of solved challenges over time)
    for a given user.

    Args:
        target_user (User): The user object for whom to generate the data.
        Submission_model: The Submission model.
        UTC_tz: The UTC timezone object.
        timedelta_obj: The timedelta object.
        get_setting_func (function): Function to retrieve application settings.

    Returns:
        dict: profile_charts_data containing challenges complete data.
    """
    profile_charts_data = {}
    if get_setting_func('PROFILE_CHALLENGES_COMPLETE_CHART_ENABLED', 'True').lower() == 'true':
        challenges_complete_data = []
        cumulative_count = 0
        submissions_for_count_chart = Submission_model.query.filter_by(user_id=target_user.id).order_by(Submission_model.timestamp.asc()).all()

        if submissions_for_count_chart:
            initial_timestamp = submissions_for_count_chart[0].timestamp - timedelta_obj(microseconds=1)
            challenges_complete_data.append({'x': initial_timestamp.isoformat(), 'y': 0})

            for submission in submissions_for_count_chart:
                cumulative_count += 1
                challenges_complete_data.append({'x': submission.timestamp.isoformat(), 'y': cumulative_count})
        else:
            challenges_complete_data.append({'x': datetime.now(UTC_tz).isoformat(), 'y': 0})
        
        profile_charts_data['challenges_complete'] = challenges_complete_data
    return profile_charts_data
