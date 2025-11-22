from flask import jsonify, g
from flask_restx import Namespace, Resource, fields, Api
from scripts.utils import api_key_required
from flask import Blueprint # Keep Blueprint for Api initialization

# Create a Blueprint that Flask-RESTX will use
api_bp = Blueprint('api_blueprint', __name__, url_prefix='/api/v1')
api_restx = Api(api_bp, doc='/doc/') # Initialize Api with the Blueprint

api_ns = Namespace('core', description='Core API operations')
api_restx.add_namespace(api_ns)

# Define a model for user output for documentation
user_model = api_ns.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'username': fields.String(required=True, description='The user\'s username'),
    'email': fields.String(description='The user\'s email address'),
    'score': fields.Integer(description='The user\'s current score'),
    'is_admin': fields.Boolean(description='Whether the user has admin privileges'),
    'last_seen': fields.DateTime(description='Timestamp of the user\'s last activity')
})

@api_ns.route('/status')
class ApiStatus(Resource):
    @api_ns.doc(security='apikey')
    @api_key_required
    def get(self):
        """
        A simple API endpoint to check API key authentication status.
        Requires an active API key.
        """
        return jsonify({
            'message': 'API key authenticated successfully!',
            'user': g.current_api_user.username
        }), 200

@api_ns.route('/users/me')
class CurrentUser(Resource):
    @api_ns.doc(security='apikey')
    @api_ns.marshal_with(user_model)
    @api_key_required
    def get(self):
        """
        Returns the profile information of the authenticated user.
        """
        user = g.current_api_user
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'score': user.score,
            'is_admin': user.is_admin,
            'last_seen': user.last_seen
        }


