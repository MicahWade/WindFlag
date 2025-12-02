from datetime import datetime, UTC
from flask import request, jsonify, current_app, g
from functools import wraps
import hashlib
import random
import os

# Import extensions as needed for the decorator
from scripts.extensions import db


def generate_usernames(num_to_generate=None):
    """
    Generates a list of usernames based on the configuration.
    If PRESET_USERNAMES_ENABLED is False, returns an empty list.
    """
    if not current_app.config.get('PRESET_USERNAMES_ENABLED', False):
        return []

    words_file_path = current_app.config.get('WORDS_FILE_PATH', 'words.txt')
    if not os.path.exists(words_file_path):
        current_app.logger.error(f"Words file not found at: {words_file_path}")
        return []

    with open(words_file_path, 'r') as f:
        words = [line.strip() for line in f if line.strip()]

    if not words:
        current_app.logger.error(f"Words file is empty: {words_file_path}")
        return []

    num_words = current_app.config.get('USERNAME_WORD_COUNT', 2)
    add_number = current_app.config.get('USERNAME_ADD_NUMBER', True)
    num_users = num_to_generate if num_to_generate is not None else current_app.config.get('PRESET_USER_COUNT', 50)

    usernames = []
    generated_unique_usernames = set() 

    while len(usernames) < num_users:
        username_words = random.choices(words, k=num_words)
        username_base = "".join(word.capitalize() for word in username_words)
        
        final_username = username_base
        if add_number:
            final_username += str(random.randint(10, 99))
        
        if final_username not in generated_unique_usernames:
            usernames.append(final_username)
            generated_unique_usernames.add(final_username)
    
    return usernames


def make_datetime_timezone_aware(dt: datetime) -> datetime:
    """
    Ensures a datetime object is timezone-aware (UTC).
    If the datetime object is naive, it's assumed to be in UTC and localized.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt

def api_key_required(f):
    """
    Decorator to protect API endpoints with API key authentication.
    The API key should be provided in the 'X-API-KEY' header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import inside the function to avoid circular dependency
        from scripts.models import ApiKey, User
        
        api_key_header = request.headers.get('X-API-KEY')

        if not api_key_header:
            current_app.logger.warning("API key missing from request headers.")
            return jsonify({'message': 'API Key is missing'}), 401

        # Check against ADMIN_API_KEY first
        admin_api_key_config = current_app.config.get('ADMIN_API_KEY')
        if admin_api_key_config and api_key_header == admin_api_key_config:
            # If it's the admin key, find an admin user and set g.current_api_user
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                g.current_api_user = admin_user
                current_app.logger.info(f"Admin API key used by user: {admin_user.username}")
                return f(*args, **kwargs)
            else:
                current_app.logger.error("ADMIN_API_KEY used, but no admin user found in database.")
                return jsonify({'message': 'ADMIN_API_KEY is configured but no admin user exists to grant permissions'}), 500

        # Hash the incoming API key for comparison
        incoming_key_hash = hashlib.sha256(api_key_header.encode('utf-8')).hexdigest()
        
        api_key_obj = ApiKey.query.filter_by(key_hash=incoming_key_hash, is_active=True).first()

        if not api_key_obj:
            current_app.logger.warning(f"Invalid or inactive API key: {api_key_header[:8]}...")
            return jsonify({'message': 'Invalid or inactive API Key'}), 401

        # Load the user associated with the API key
        user = User.query.get(api_key_obj.user_id)
        if not user:
            current_app.logger.error(f"User for API key {api_key_obj.id} not found.")
            return jsonify({'message': 'Associated user not found'}), 401
        
        # Update last_used_at timestamp
        api_key_obj.last_used_at = datetime.now(UTC)
        db.session.add(api_key_obj)
        db.session.commit()

        # Make the user object available to the decorated function
        g.current_api_user = user
        return f(*args, **kwargs)
    return decorated_function
