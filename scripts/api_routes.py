from flask import jsonify, g, request
from flask_restx import Namespace, Resource, fields, Api
from scripts.utils import api_key_required
from flask import Blueprint # Keep Blueprint for Api initialization
from scripts.models import Challenge # Import Challenge model

# Create a Blueprint that Flask-RESTX will use
api_bp = Blueprint('api_blueprint', __name__, url_prefix='/api/v1')

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    },
    'dynamic_flag_apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Dynamic-Flag-API-KEY'
    }
}

api_restx = Api(api_bp, doc='/doc/', authorizations=authorizations) # Initialize Api with the Blueprint and authorizations

api_ns = Namespace('core', description='Core API operations')
challenges_ns = Namespace('challenges', description='Operations related to challenges')

api_restx.add_namespace(api_ns)
api_restx.add_namespace(challenges_ns)

# Define a model for user output for documentation
user_model = api_ns.model('User', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'username': fields.String(required=True, description='The user\'s username'),
    'email': fields.String(description='The user\'s email address'),
    'score': fields.Integer(description='The user\'s current score'),
    'is_admin': fields.Boolean(description='Whether the user has admin privileges'),
    'last_seen': fields.DateTime(description='Timestamp of the user\'s last activity')
})

# Define a model for dynamic flag response
dynamic_flag_model = challenges_ns.model('DynamicFlag', {
    'challenge_id': fields.Integer(description='The ID of the challenge'),
    'dynamic_flag': fields.String(description='The dynamically generated flag')
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

@challenges_ns.route('/<int:challenge_id>/dynamic_flag')
@challenges_ns.param('challenge_id', 'The unique identifier of the challenge')
class DynamicFlag(Resource):
    @challenges_ns.doc(
        description='Retrieves a dynamic flag for a specific challenge. Requires a challenge-specific API key.',
        security='dynamic_flag_apikey',
        params={'X-Dynamic-Flag-API-KEY': {'description': 'Challenge-specific API Key', 'type': 'string', 'in': 'header', 'required': True}}
    )
    @challenges_ns.marshal_with(dynamic_flag_model)
    def get(self, challenge_id):
        """
        Retrieves a dynamic flag for a specific challenge.
        """
        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            challenges_ns.abort(404, message=f"Challenge with ID {challenge_id} not found.")

        if not challenge.has_dynamic_flag:
            challenges_ns.abort(403, message=f"Challenge {challenge_id} does not support dynamic flags.")

        # Authenticate using the challenge-specific API key
        dynamic_flag_api_key_header = request.headers.get('X-Dynamic-Flag-API-KEY')
        if not dynamic_flag_api_key_header:
            challenges_ns.abort(401, message="Dynamic Flag API Key is missing.")

        if not challenge.verify_dynamic_flag_api_key(dynamic_flag_api_key_header):
            challenges_ns.abort(401, message="Invalid Dynamic Flag API Key.")

        # Generate and return the dynamic flag
        # In a real scenario, you'd want to pass a user ID here if the flag is user-specific.
        # For simplicity, we'll use a dummy user_id for now.
        # This assumes the user requesting the flag has already solved/unlocked the challenge.
        # A more robust solution might integrate with the user's solved challenges.
        dynamic_flag = challenge.generate_dynamic_flag(user_id="anonymous") # Placeholder user_id

        return {
            'challenge_id': challenge.id,
            'dynamic_flag': dynamic_flag
        }


