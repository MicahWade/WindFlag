from datetime import datetime, UTC
from flask import request, jsonify, current_app, g
from functools import wraps
import hashlib

# Import extensions as needed for the decorator
from scripts.extensions import db


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
