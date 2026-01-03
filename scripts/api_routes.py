"""
This module defines the API routes and functions for the WindFlag CTF platform.
"""
from flask import Blueprint, request, jsonify, g
from flask_login import current_user, login_required
from scripts.extensions import db
from scripts.models import Challenge, Category, ChallengeFlag, Submission, User, AwardCategory, Setting, CHALLENGE_TYPES, UserHint, FlagSubmission, TestCase
from scripts.utils import api_key_required
from scripts.code_execution import execute_code_in_sandbox, CodeExecutionResult
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')

def admin_api_required(f):
    """
    Decorator to ensure that only authenticated administrators can access an API route.
    """
    @wraps(f)
    @api_key_required
    def decorated_function(*args, **kwargs):
        if not g.current_api_user.is_admin:
            return jsonify({'message': 'Administrator access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/verify_challenge_access', methods=['POST'])
def verify_challenge_access():
    """
    Verifies if a user (via API Key) has access to a specific challenge.
    """
    from flask import current_app
    data = request.get_json()
    if not data or not all(k in data for k in ['api_key', 'category', 'challenge_id']):
        current_app.logger.warning("verify_challenge_access: Missing required fields")
        return jsonify({'allowed': False, 'message': 'Missing required fields'}), 400

    plain_api_key = data['api_key']
    category_name = data['category']
    challenge_name = data['challenge_id'] # SwitchBoard sends 'challenge_id' which is often the name or an ID. Let's assume name for now based on SB logic.
    
    current_app.logger.info(f"verify_challenge_access called for user (key prefix: {plain_api_key[:4] if plain_api_key else 'None'}). Cat: {category_name}, Chal: {challenge_name}")

    # Hash the key to look it up
    import hashlib
    key_hash = hashlib.sha256(plain_api_key.encode('utf-8')).hexdigest()
    
    from scripts.models import ApiKey
    api_key_entry = ApiKey.query.filter_by(key_hash=key_hash, is_active=True).first()
    
    if not api_key_entry:
        current_app.logger.warning("verify_challenge_access: Invalid API Key")
        return jsonify({'allowed': False, 'message': 'Invalid API Key'}), 401

    user = User.query.get(api_key_entry.user_id)
    if not user:
        current_app.logger.warning("verify_challenge_access: User not found for API Key")
        return jsonify({'allowed': False, 'message': 'User not found'}), 401
    
    current_app.logger.info(f"User identified: {user.username} (ID: {user.id})")

    # Find the challenge
    # SwitchBoard uses category name and challenge_id (which maps to challenge name usually in SB DB)
    # We need to find the challenge by name and category name
    category = Category.query.filter_by(name=category_name).first()
    
    # Fallback: Try replacing underscores with spaces for Category
    if not category:
        category = Category.query.filter_by(name=category_name.replace('_', ' ')).first()

    # Fallback: Try case-insensitive match for Category
    if not category:
        category = Category.query.filter(Category.name.ilike(category_name.replace('_', ' '))).first()

    if not category:
         current_app.logger.warning(f"verify_challenge_access: Category '{category_name}' not found (even with fallbacks)")
         return jsonify({'allowed': False, 'message': 'Category not found'}), 404
    
    current_app.logger.info(f"Category found: {category.name} (ID: {category.id})")

    # Try to match challenge by name (SwitchBoard often uses name as ID in URL)
    # OR by ID if it's an integer. SwitchBoard 'challenge_id' is a string from URL.
    challenge = Challenge.query.filter_by(name=challenge_name, category_id=category.id).first()
    
    # Fallback: Try replacing underscores with spaces for Challenge Name
    if not challenge:
        challenge = Challenge.query.filter_by(name=challenge_name.replace('_', ' '), category_id=category.id).first()

    # Fallback: Try case-insensitive match for Challenge Name
    if not challenge:
        challenge = Challenge.query.filter(Challenge.name.ilike(challenge_name.replace('_', ' ')), Challenge.category_id == category.id).first()
    
    if not challenge:
        # Fallback: check if challenge_name is actually an ID
        if challenge_name.isdigit():
             challenge = Challenge.query.filter_by(id=int(challenge_name), category_id=category.id).first()

    if not challenge:
        current_app.logger.warning(f"verify_challenge_access: Challenge '{challenge_name}' not found in category {category.name}")
        return jsonify({'allowed': False, 'message': 'Challenge not found'}), 404

    current_app.logger.info(f"Challenge found: {challenge.name} (ID: {challenge.id}). Checking access...")

    # Check access
    # We need to build the cache expected by is_unlocked_for_user
    solved_challenges = {sub.challenge_id for sub in user.submissions}
    user_completed_challenges_cache = {user.id: solved_challenges}
    
    is_unlocked = challenge.is_unlocked_for_user(user, user_completed_challenges_cache)
    current_app.logger.info(f"is_unlocked_for_user result: {is_unlocked}")

    if is_unlocked:
        return jsonify({'allowed': True, 'user_id': user.id}), 200
    else:
        # Log reason for failure
        current_app.logger.info(f"Access Denied Logic Check: UnlockType={challenge.unlock_type}, Hidden={challenge.is_hidden}, CatHidden={category.is_hidden}, Prereqs={challenge.prerequisite_challenge_ids}")
        return jsonify({'allowed': False, 'message': "You can't access this challenge yet."}), 403

@api_bp.route('/admin/import/yaml', methods=['POST'])
@admin_api_required
def import_yaml():
    """
    Imports challenges and categories from a YAML string provided in the request body.
    Requires admin API access.
    """
    yaml_content = request.data.decode('utf-8') # Get raw YAML content from request body

    if not yaml_content:
        return jsonify({'message': 'Request body must contain YAML content'}), 400

    from flask import current_app # Import current_app to pass to import functions
    from scripts.import_export import import_categories_from_yaml, import_challenges_from_yaml

    # Use a list to capture messages from import functions
    import_messages = []

    def custom_print(*args, **kwargs):
        """Custom print function to capture output."""
        message = " ".join(map(str, args))
        import_messages.append(message)
        # Also print to console for server logs
        current_app.logger.info(message)

    # Temporarily redirect print to capture output
    import builtins
    original_print = builtins.print
    builtins.print = custom_print

    try:
        # It's generally safer to import categories first, then challenges
        import_categories_from_yaml(current_app, yaml_content, is_file=False)
        import_challenges_from_yaml(current_app, yaml_content, is_file=False)
        
        # Check if any errors or warnings occurred during import
        if any("Error:" in msg for msg in import_messages):
            status_code = 400
            overall_message = "YAML import completed with errors or warnings. Check messages for details."
        else:
            status_code = 200
            overall_message = "YAML import completed successfully."

        return jsonify({'message': overall_message, 'details': import_messages}), status_code

    except Exception as e:
        current_app.logger.error(f"Error during YAML import API call: {e}", exc_info=True)
        return jsonify({'message': f'An unexpected error occurred during YAML import: {str(e)}'}), 500
    finally:
        # Restore original print function
        builtins.print = original_print


@api_bp.route('/challenges', methods=['POST'])
@admin_api_required
def create_challenge():
    """
    Creates a new challenge.
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body must be JSON'}), 400

    required_fields = ['name', 'description', 'points', 'category_id']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    challenge = Challenge(
        name=data['name'],
        description=data['description'],
        points=data['points'],
        category_id=data['category_id'],
        case_sensitive=data.get('case_sensitive', True),
        multi_flag_type=data.get('multi_flag_type', 'SINGLE'),
        multi_flag_threshold=data.get('multi_flag_threshold'),
        point_decay_type=data.get('point_decay_type', 'STATIC'),
        point_decay_rate=data.get('point_decay_rate'),
        proactive_decay=data.get('proactive_decay', False),
        minimum_points=data.get('minimum_points', 1),
        unlock_type=data.get('unlock_type', 'NONE'),
        prerequisite_percentage_value=data.get('prerequisite_percentage_value'),
        prerequisite_count_value=data.get('prerequisite_count_value'),
        prerequisite_count_category_ids=data.get('prerequisite_count_category_ids'),
        prerequisite_challenge_ids=data.get('prerequisite_challenge_ids'),
        unlock_date_time=data.get('unlock_date_time'),
        expiration_date=data.get('expiration_date'),
        unlock_point_reduction_type=data.get('unlock_point_reduction_type'),
        unlock_point_reduction_value=data.get('unlock_point_reduction_value'),
        unlock_point_reduction_target_date=data.get('unlock_point_reduction_target_date'),
        is_hidden=data.get('is_hidden', False),
        has_dynamic_flag=data.get('has_dynamic_flag', False),
        challenge_type=data.get('challenge_type', 'FLAG'),
        language=data.get('language'),
        starter_code=data.get('starter_code'),
        setup_code=data.get('setup_code')
    )
    db.session.add(challenge)
    db.session.commit() # Commit challenge first to get its ID

    if 'test_cases' in data and isinstance(data['test_cases'], list):
        for i, tc_data in enumerate(data['test_cases']):
            test_case = TestCase(
                challenge_id=challenge.id,
                input_data=tc_data.get('input_data'),
                expected_output=tc_data.get('expected_output'),
                order=i
            )
            db.session.add(test_case)
        db.session.commit() # Commit all test cases

    if 'flags' in data and isinstance(data['flags'], list):
        for flag_content in data['flags']:
            challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
            db.session.add(challenge_flag)
        db.session.commit() # Commit all flags

    return jsonify({
        'message': 'Challenge created successfully',
        'challenge': {
            'id': challenge.id,
            'name': challenge.name
        }
    }), 201


@api_bp.route('/public/challenges', methods=['GET'])
@login_required
def get_public_challenges():
    """
    Gets a list of all challenges for the public API.
    """
    categories = Category.query.order_by(Category.name).all()
    solved_challenges = {sub.challenge_id for sub in current_user.submissions}
    
    # Pre-fetch all submissions to optimize
    all_submissions = Submission.query.all()
    solves_per_challenge = {}
    for sub in all_submissions:
        solves_per_challenge[sub.challenge_id] = solves_per_challenge.get(sub.challenge_id, 0) + 1

    # Create a cache for the current user's completed challenges to pass to is_unlocked_for_user
    user_completed_challenges_cache = {current_user.id: solved_challenges}

    category_data = []
    for category in categories:
        challenges_data = []
        for challenge in category.challenges:
            # Use the model's logic to determine if the challenge should be visible
            if challenge.is_unlocked_for_user(current_user, user_completed_challenges_cache):
                challenges_data.append({
                    'id': challenge.id,
                    'name': challenge.name,
                    'points': challenge.points,
                    'description': challenge.description,
                    'solved': challenge.id in solved_challenges,
                    'solves': solves_per_challenge.get(challenge.id, 0),
                    'category': category.name,
                    'challenge_type': challenge.challenge_type,
                    'language': challenge.language,
                    'starter_code': challenge.starter_code
                })
        if challenges_data:
            category_data.append({
                'name': category.name,
                'challenges': challenges_data
            })
    
    return jsonify(category_data)

@api_bp.route('/challenge_details/<int:challenge_id>', methods=['GET'])
@login_required
def get_challenge_details_for_modal(challenge_id):
    """
    Gets details for a single challenge to display in the modal.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Check if the challenge is hidden from the current user
    # For now, let's assume if it's hidden, we just return a message,
    # or handle it upstream. The JS already handles a "success: false" response.
    if challenge.is_hidden and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Challenge not found or not accessible.'}), 404

    # Check if the user has already solved this challenge
    is_completed = Submission.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge.id
    ).first() is not None

    # Get hints, revealing if user has already paid for them
    hints_data = []
    for hint in challenge.hints:
        user_hint = UserHint.query.filter_by(hint_id=hint.id, user_id=current_user.id).first()
        hints_data.append({
            'id': hint.id,
            'title': hint.title,
            'content': hint.content if user_hint else None,
            'cost': hint.cost,
            'is_revealed': user_hint is not None
        })

    # Get flags submitted count for multi-flag challenges
    submitted_flags_count = 0
    total_flags = 0
    if challenge.multi_flag_type != 'SINGLE':
        submitted_flags_count = FlagSubmission.query.filter_by(
            user_id=current_user.id,
            challenge_id=challenge.id
        ).count()
        total_flags = len(challenge.flags)

    return jsonify({
        'success': True,
        'id': challenge.id,
        'name': challenge.name,
        'description': challenge.description,
        'points': challenge.points,
        'is_completed': is_completed,
        'multi_flag_type': challenge.multi_flag_type,
        'submitted_flags_count': submitted_flags_count,
        'total_flags': total_flags,
        'hints': hints_data,
        'challenge_type': challenge.challenge_type,
        'language': challenge.language,
        'starter_code': challenge.starter_code
    }), 200


@api_bp.route('/challenges', methods=['GET'])
@admin_api_required
def get_challenges():
    """
    Gets a list of all challenges.
    """
    challenges = Challenge.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'points': c.points, 'challenge_type': c.challenge_type, 'language': c.language, 'starter_code': c.starter_code} for c in challenges])


@api_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@admin_api_required
def get_challenge(challenge_id):
    """
    Gets a single challenge by its ID.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    return jsonify({
        'id': challenge.id,
        'name': challenge.name,
        'description': challenge.description,
        'points': challenge.points,
        'category_id': challenge.category_id,
        'case_sensitive': challenge.case_sensitive,
        'multi_flag_type': challenge.multi_flag_type,
        'multi_flag_threshold': challenge.multi_flag_threshold,
        'point_decay_type': challenge.point_decay_type,
        'point_decay_rate': challenge.point_decay_rate,
        'proactive_decay': challenge.proactive_decay,
        'minimum_points': challenge.minimum_points,
        'unlock_type': challenge.unlock_type,
        'prerequisite_percentage_value': challenge.prerequisite_percentage_value,
        'prerequisite_count_value': challenge.prerequisite_count_value,
        'prerequisite_count_category_ids': challenge.prerequisite_count_category_ids,
        'prerequisite_challenge_ids': challenge.prerequisite_challenge_ids,
        'unlock_date_time': challenge.unlock_date_time,
        'expiration_date': challenge.expiration_date,
        'unlock_point_reduction_type': challenge.unlock_point_reduction_type,
        'unlock_point_reduction_value': challenge.unlock_point_reduction_value,
        'unlock_point_reduction_target_date': challenge.unlock_point_reduction_target_date,
        'is_hidden': challenge.is_hidden,
        'has_dynamic_flag': challenge.has_dynamic_flag,
        'challenge_type': challenge.challenge_type,
        'language': challenge.language,
        'starter_code': challenge.starter_code,
        'flags': [{'id': f.id, 'content': f.flag_content} for f in challenge.flags],
        'test_cases': [{'id': tc.id, 'input_data': tc.input_data, 'expected_output': tc.expected_output, 'order': tc.order} for tc in sorted(challenge.test_cases, key=lambda tc: tc.order)]
    })


@api_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@admin_api_required
def update_challenge_api(challenge_id):
    """
    Updates a challenge.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body must be JSON'}), 400

    for field in ['name', 'description', 'points', 'category_id', 'case_sensitive', 'multi_flag_type', 'multi_flag_threshold', 'point_decay_type', 'point_decay_rate', 'proactive_decay', 'minimum_points', 'unlock_type', 'prerequisite_percentage_value', 'prerequisite_count_value', 'prerequisite_count_category_ids', 'prerequisite_challenge_ids', 'unlock_date_time', 'expiration_date', 'unlock_point_reduction_type', 'unlock_point_reduction_value', 'unlock_point_reduction_target_date', 'is_hidden', 'has_dynamic_flag', 'challenge_type', 'language', 'starter_code', 'setup_code']:
        if field in data:
            setattr(challenge, field, data[field])

    if 'flags' in data and isinstance(data['flags'], list):
        ChallengeFlag.query.filter_by(challenge_id=challenge.id).delete()
        for flag_content in data['flags']:
            challenge_flag = ChallengeFlag(challenge_id=challenge.id, flag_content=flag_content)
            db.session.add(challenge_flag)

    # Handle test cases
    if 'test_cases' in data and isinstance(data['test_cases'], list):
        # Delete existing test cases
        TestCase.query.filter_by(challenge_id=challenge.id).delete()
        
        # Add new test cases
        for i, tc_data in enumerate(data['test_cases']):
            test_case = TestCase(
                challenge_id=challenge.id,
                input_data=tc_data.get('input_data'),
                expected_output=tc_data.get('expected_output'),
                order=i
            )
            db.session.add(test_case)

    db.session.commit()
    return jsonify({'message': 'Challenge updated successfully'})

@api_bp.route('/admin/verify_coding_challenge', methods=['POST'])
@login_required
def verify_coding_challenge():
    """
    Verifies a coding challenge's reference solution against its defined test cases for administrators.
    """
    if not current_user.is_admin:
        return jsonify({'message': 'Administrator access required'}), 403

    data = request.get_json()
    if not data or 'challenge_id' not in data:
        return jsonify({'message': 'Request body must be JSON and include "challenge_id"'}), 400

    challenge_id = data['challenge_id']
    challenge = Challenge.query.get_or_404(challenge_id)

    if challenge.challenge_type != 'CODING':
        return jsonify({'message': 'This is not a coding challenge.'}), 400
    
    if not challenge.reference_solution:
        return jsonify({'message': 'No reference solution defined for this challenge.'}), 400

    test_cases = challenge.test_cases
    if not test_cases:
        return jsonify({'message': 'No test cases defined for this coding challenge.'}), 400

    all_test_cases_passed = True
    test_case_results = []

    sorted_test_cases = sorted(test_cases, key=lambda tc: tc.order)

    for test_case in sorted_test_cases:
        execution_result = execute_code_in_sandbox(
            language=challenge.language,
            code=challenge.reference_solution,
            expected_output=test_case.expected_output,
            setup_code=challenge.setup_code,
            test_case_input=test_case.input_data,
        )

        test_case_passed = execution_result.success
        if not test_case_passed:
            all_test_cases_passed = False

        test_case_results.append({
            'test_case_id': test_case.id,
            'input_data': test_case.input_data,
            'expected_output': test_case.expected_output,
            'actual_output': execution_result.stdout,
            'passed': test_case_passed,
            'error_message': execution_result.error_message,
            'is_timeout': execution_result.is_timeout,
            'stderr': execution_result.stderr
        })
    
    # Update solution_verified status of the challenge
    challenge.solution_verified = all_test_cases_passed
    db.session.commit()

    if all_test_cases_passed:
        return jsonify({
            'message': 'Reference solution verified successfully against all test cases.',
            'is_correct': True,
            'success': True,
            'test_case_results': test_case_results
        }), 200
    else:
        return jsonify({
            'message': 'Reference solution failed some test cases.',
            'is_correct': False,
            'success': False,
            'test_case_results': test_case_results
        }), 200


@api_bp.route('/challenges/<int:challenge_id>/submit_code', methods=['POST'])
@login_required # User must be logged in
def submit_code_challenge(challenge_id):
    """
    Submits code for a coding challenge and runs it against multiple test cases.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    if challenge.challenge_type != 'CODING':
        return jsonify({'message': 'This is not a coding challenge.'}), 400

    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({'message': 'Request body must be JSON and include "code"'}), 400

    user_code = data['code']

    test_cases = challenge.test_cases # Access the relationship
    if not test_cases:
        return jsonify({'message': 'No test cases defined for this coding challenge.'}), 400

    all_test_cases_passed = True
    test_case_results = []

    # Sort test cases by their 'order' field
    sorted_test_cases = sorted(test_cases, key=lambda tc: tc.order)

    for test_case in sorted_test_cases:
        execution_result = execute_code_in_sandbox(
            language=challenge.language,
            code=user_code,
            expected_output=test_case.expected_output,
            setup_code=challenge.setup_code,
            test_case_input=test_case.input_data,
        )

        test_case_passed = execution_result.success
        if not test_case_passed:
            all_test_cases_passed = False

        test_case_results.append({
            'test_case_id': test_case.id,
            'input_data': test_case.input_data,
            'expected_output': test_case.expected_output,
            'actual_output': execution_result.stdout,
            'passed': test_case_passed,
            'error_message': execution_result.error_message,
            'is_timeout': execution_result.is_timeout,
            'stderr': execution_result.stderr
        })

    if all_test_cases_passed:
        # Check if the user has already solved this challenge
        existing_submission = Submission.query.filter_by(
            user_id=current_user.id,
            challenge_id=challenge.id
        ).first()

        if not existing_submission:
            # Mark challenge as solved for the user
            new_submission = Submission(
                user_id=current_user.id,
                challenge_id=challenge.id,
                score_at_submission=challenge.points # Store current points
            )
            db.session.add(new_submission)
            current_user.score += challenge.points
            db.session.commit()
            return jsonify({
                'message': 'Challenge solved! All test cases passed.',
                'is_correct': True,
                'success': True,
                'test_case_results': test_case_results
            }), 200
        else:
            return jsonify({
                'message': 'Challenge already solved! All test cases passed.',
                'is_correct': True,
                'success': True,
                'test_case_results': test_case_results
            }), 200
    else:
        # Provide feedback on why it failed
        return jsonify({
            'message': 'Some test cases failed.',
            'is_correct': False,
            'success': False,
            'test_case_results': test_case_results
        }), 200


@api_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@admin_api_required
def delete_challenge_api(challenge_id):
    """
    Deletes a challenge.
    """
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    return jsonify({'message': 'Challenge deleted successfully'})

# Category Endpoints
@api_bp.route('/categories', methods=['GET'])
@admin_api_required
def get_categories():
    """
    Gets a list of all categories.
    """
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@api_bp.route('/categories/<int:category_id>', methods=['GET'])
@admin_api_required
def get_category(category_id):
    """
    Gets a single category by its ID.
    """
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name
    })

@api_bp.route('/categories', methods=['POST'])
@admin_api_required
def create_category():
    """
    Creates a new category.
    """
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'message': 'Request body must be JSON and include a name'}), 400

    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'Category created successfully', 'category': {'id': category.id, 'name': category.name}}), 201

@api_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_api_required
def update_category_api(category_id):
    """
    Updates a category.
    """
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body must be JSON'}), 400

    if 'name' in data:
        category.name = data['name']
    
    db.session.commit()
    return jsonify({'message': 'Category updated successfully'})

@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@api_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_api_required
def delete_category_api(category_id):
    """
    Deletes a category.
    """
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})

# User Endpoints
@api_bp.route('/users', methods=['GET'])
@admin_api_required
def get_users():
    """
    Gets a list of all users.
    """
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'email': u.email, 'is_admin': u.is_admin, 'is_hidden': u.hidden} for u in users])

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_api_required
def get_user(user_id):
    """
    Gets a single user by ID.
    """
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_hidden': user.hidden
    })

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_api_required
def update_user(user_id):
    """
    Updates a user.
    """
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body must be JSON'}), 400

    if 'is_hidden' in data:
        user.is_hidden = data['is_hidden']
    
    if 'is_admin' in data:
        user.is_admin = data['is_admin']

    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

# Award Category Endpoints
@api_bp.route('/award_categories', methods=['GET'])
@admin_api_required
def get_award_categories():
    """
    Gets a list of all award categories.
    """
    award_categories = AwardCategory.query.all()
    return jsonify([{'id': ac.id, 'name': ac.name, 'default_points': ac.default_points} for ac in award_categories])

@api_bp.route('/award_categories/<int:category_id>', methods=['GET'])
@admin_api_required
def get_award_category(category_id):
    """
    Gets a single award category by ID.
    """
    award_category = AwardCategory.query.get_or_404(category_id)
    return jsonify({
        'id': award_category.id,
        'name': award_category.name,
        'default_points': award_category.default_points
    })

@api_bp.route('/award_categories', methods=['POST'])
@admin_api_required
def create_award_category():
    """
    Creates a new award category.
    """
    data = request.get_json()
    if not data or 'name' not in data or 'default_points' not in data:
        return jsonify({'message': 'Request body must be JSON and include name and default_points'}), 400

    award_category = AwardCategory(name=data['name'], default_points=data['default_points'])
    db.session.add(award_category)
    db.session.commit()
    return jsonify({'message': 'Award category created successfully', 'award_category': {'id': award_category.id, 'name': award_category.name, 'default_points': award_category.default_points}}), 201

@api_bp.route('/award_categories/<int:category_id>', methods=['PUT'])
@admin_api_required
def update_award_category_api(category_id):
    """
    Updates an award category.
    """
    award_category = AwardCategory.query.get_or_404(category_id)
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Request body must be JSON'}), 400

    if 'name' in data:
        award_category.name = data['name']
    if 'default_points' in data:
        award_category.default_points = data['default_points']
    
    db.session.commit()
    return jsonify({'message': 'Award category updated successfully'})

@api_bp.route('/award_categories/<int:category_id>', methods=['DELETE'])
@admin_api_required
def delete_award_category_api(category_id):
    """
    Deletes an award category.
    """
    award_category = AwardCategory.query.get_or_404(category_id)
    if award_category.awards:
        return jsonify({'message': 'Cannot delete category with associated awards. Please delete awards first.'}), 400
    db.session.delete(award_category)
    db.session.commit()
    return jsonify({'message': 'Award category deleted successfully'})

# Award Endpoints
@api_bp.route('/awards', methods=['POST'])
@admin_api_required
def give_award():
    """
    Gives an award to a user.
    """
    data = request.get_json()
    if not data or 'user_id' not in data or 'category_id' not in data or 'points_awarded' not in data:
        return jsonify({'message': 'Request body must be JSON and include user_id, category_id, and points_awarded'}), 400

    user = User.query.get_or_404(data['user_id'])
    award_category = AwardCategory.query.get_or_404(data['category_id'])

    award = Award(
        user_id=user.id,
        category_id=award_category.id,
        points_awarded=data['points_awarded'],
        admin_id=g.current_api_user.id # Admin making the API call
    )
    db.session.add(award)
    user.score += data['points_awarded']
    db.session.commit()
    return jsonify({'message': 'Award given successfully', 'award': {'id': award.id, 'user_id': award.user_id, 'category_id': award.category_id, 'points_awarded': award.points_awarded}}), 201

# Setting Endpoints
@api_bp.route('/settings', methods=['GET'])
@admin_api_required
def get_settings():
    """
    Gets all settings.
    """
    settings = Setting.query.all()
    return jsonify([{'key': s.key, 'value': s.value} for s in settings])

@api_bp.route('/settings', methods=['PUT'])
@admin_api_required
def update_setting():
    """
    Updates a setting.
    """
    data = request.get_json()
    if not data or 'key' not in data or 'value' not in data:
        return jsonify({'message': 'Request body must be JSON and include key and value'}), 400

    setting = Setting.query.filter_by(key=data['key']).first()
    if setting:
        setting.value = data['value']
    else:
        setting = Setting(key=data['key'], value=data['value'])
        db.session.add(setting)
    db.session.commit()
    return jsonify({'message': 'Setting updated successfully'})

# Submission Endpoints
@api_bp.route('/submissions', methods=['GET'])
@admin_api_required
def get_submissions():
    """
    Gets all submissions.
    """
    submissions = Submission.query.all()
    return jsonify([{'id': s.id, 'user_id': s.user_id, 'challenge_id': s.challenge_id, 'timestamp': s.timestamp, 'score_at_submission': s.score_at_submission} for s in submissions])

# Analytics Endpoints
@api_bp.route('/analytics', methods=['GET'])
@admin_api_required
def get_analytics():
    """
    Gets all analytics data.
    """
    # Import necessary functions from admin_routes to reuse logic
    from scripts.admin_routes import _get_challenge_points_by_category, _get_award_points_by_category, _get_challenge_points_by_user, _get_award_points_by_user, _get_challenges_solved_over_time, _get_fails_vs_succeeds_data, _get_challenge_solve_counts, _get_user_challenge_matrix_data
    from scripts.chart_data_utils import get_global_score_history_data

    # Data for Points by Category
    challenge_points_by_category = _get_challenge_points_by_category()
    total_award_points = _get_award_points_by_category()
    
    category_data = {name: points for name, points in challenge_points_by_category}
    if total_award_points:
        category_data['Awards'] = category_data.get('Awards', 0) + total_award_points

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    # Data for Points by User
    challenge_points_by_user = _get_challenge_points_by_user()
    award_points_by_user = _get_award_points_by_user()

    user_data = {username: points for username, points in challenge_points_by_user}
    for username, points in award_points_by_user:
        user_data[username] = user_data.get(username, 0) + points
    
    user_labels = list(user_data.keys())
    user_values = list(user_data.values())

    # Data for Challenges Solved Over Time
    challenges_solved_over_time = _get_challenges_solved_over_time()
    solved_dates = [str(date) for date, _ in challenges_solved_over_time]
    solved_counts = [count for _, count in challenges_solved_over_time]

    # Data for Challenge Points Over Time Chart (Cumulative Score)
    global_chart_data = get_global_score_history_data()

    if global_chart_data:
        global_stats_over_time = global_chart_data.get('global_stats_over_time', [])
        user_scores_over_time = global_chart_data.get('user_scores_over_time', {})
    else:
        global_stats_over_time = []
        user_scores_over_time = {}

    cumulative_points_dates = [item['x'] for item in global_stats_over_time]
    cumulative_points_values = [item['avg'] for item in global_stats_over_time]

    # Data for Fails vs Succeeds
    total_successful_flag_attempts, total_failed_flag_attempts = _get_fails_vs_succeeds_data()
    fails_succeeds_labels = ['Succeeds', 'Fails']
    fails_succeeds_values = [total_successful_flag_attempts, total_failed_flag_attempts]

    # Data for Challenges Solved Count (for bar graph)
    challenge_solve_counts = _get_challenge_solve_counts()
    challenge_solve_labels = [name for name, count in challenge_solve_counts]
    challenge_solve_values = [count for name, count in challenge_solve_counts]

    # Data for User-Challenge Matrix Table
    all_users, all_challenges, user_challenge_status = _get_user_challenge_matrix_data()

    return jsonify({
        'category_data': {'labels': category_labels, 'values': category_values},
        'user_data': {'labels': user_labels, 'values': user_values},
        'challenges_solved_over_time': {'dates': solved_dates, 'counts': solved_counts},
        'cumulative_points_over_time': {'dates': cumulative_points_dates, 'values': cumulative_points_values},
        'fails_vs_succeeds': {'labels': fails_succeeds_labels, 'values': fails_succeeds_values},
        'challenge_solve_counts': {'labels': challenge_solve_labels, 'values': challenge_solve_values},
        'user_challenge_matrix': {
            'users': [{'id': u.id, 'username': u.username} for u in all_users],
            'challenges': [{'id': c.id, 'name': c.name} for c in all_challenges],
            'status': user_challenge_status
        }
    })