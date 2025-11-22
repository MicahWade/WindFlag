from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from scripts.extensions import db
from scripts.models import ApiKey
import secrets
import hashlib
from datetime import datetime, UTC

api_key_bp = Blueprint('api_key', __name__, url_prefix='/user/api_keys')

@api_key_bp.route('/', methods=['GET'])
@login_required
def manage_api_keys():
    """
    Displays the user's API keys.
    """
    user_api_keys = ApiKey.query.filter_by(user_id=current_user.id).all()
    # In a real application, you might render a template here.
    # For now, let's just return JSON.
    return jsonify([
        {
            'id': key.id,
            'key_prefix': key.key_hash[:8] + '...', # Only show a prefix for security
            'created_at': key.created_at,
            'last_used_at': key.last_used_at,
            'is_active': key.is_active
        } for key in user_api_keys
    ])

@api_key_bp.route('/generate', methods=['POST'])
@login_required
def generate_api_key():
    """
    Generates a new API key for the current user.
    """
    if not current_user.is_authenticated:
        return jsonify({'message': 'Authentication required'}), 401

    raw_key = secrets.token_urlsafe(32) # Generate a random, URL-safe key
    key_hash = hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    new_api_key = ApiKey(
        user_id=current_user.id,
        key_hash=key_hash,
        created_at=datetime.now(UTC),
        is_active=True
    )
    db.session.add(new_api_key)
    db.session.commit()

    # The raw key is returned ONLY ONCE. The user must save it.
    flash('Your new API key has been generated. Please save it now as it will not be shown again.', 'success')
    return jsonify({
        'message': 'API key generated successfully.',
        'api_key': raw_key, # WARNING: This is the ONLY time the user sees the raw key!
        'key_id': new_api_key.id
    }), 201

@api_key_bp.route('/<int:key_id>/revoke', methods=['POST'])
@login_required
def revoke_api_key(key_id):
    """
    Revokes (deactivates) an API key for the current user.
    """
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'message': 'API Key not found or not authorized'}), 404

    api_key.is_active = False
    db.session.commit()
    flash('API key revoked successfully.', 'info')
    return jsonify({'message': 'API Key revoked.'}), 200

@api_key_bp.route('/<int:key_id>/activate', methods=['POST'])
@login_required
def activate_api_key(key_id):
    """
    Activates an inactive API key for the current user.
    """
    api_key = ApiKey.query.filter_by(id=key_id, user_id=current_user.id).first()
    if not api_key:
        return jsonify({'message': 'API Key not found or not authorized'}), 404

    api_key.is_active = True
    db.session.commit()
    flash('API key activated successfully.', 'info')
    return jsonify({'message': 'API Key activated.'}), 200

