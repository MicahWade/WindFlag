from datetime import datetime, timedelta, UTC
from collections import defaultdict
import numpy as np
from sqlalchemy.orm import joinedload
from scripts.extensions import db
from scripts.models import User, Submission, Challenge, Award

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
                scores_np = np.array(eligible_scores)
                q1, q3 = np.percentile(scores_np, [25, 75])
                avg = float(np.mean(scores_np))
                std_dev = float(np.std(scores_np))
                
                # Apply floor for -1 Std Dev
                minus_one_std_dev_val = max(-1.0, avg - std_dev)

                global_stats_over_time.append({
                    'x': datetime.combine(current_day, datetime.min.time(), tzinfo=UTC).isoformat(),
                    'min': float(np.min(scores_np)),
                    'max': float(np.max(scores_np)),
                    'avg': avg,
                    'std_dev': std_dev,
                    'q1': float(q1),
                    'q3': float(q3)
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
