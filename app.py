"""
Main application file for the WindFlag CTF platform.

This file initializes the Flask application, configures extensions, and registers blueprints.
"""
import os
import argparse
import threading
import sys
import mimetypes
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, url_for, send_from_directory, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env file in the project root
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'))

from scripts.config import Config
from scripts.extensions import db, login_manager, bcrypt
from scripts.admin_routes import admin_bp
from scripts.api_key_routes import api_key_bp
from scripts.api_routes import api_bp
from scripts.core_routes import core_bp
from scripts.theme_utils import get_active_theme

def create_app(config_class=Config):
    """
    Initializes and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['APP_NAME'] = os.getenv('APP_NAME', 'WindFlag')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.unauthorized_handler(lambda: redirect(url_for('core.home')))
    bcrypt.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        app.config['ACTIVE_THEME'] = get_active_theme()
    
    # Initialize Flask-Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        storage_uri="memory://",
        strategy="moving-window"
    )

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'message': f"Ratelimit exceeded: {e.description}"}), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        current_app.logger.exception(f"Internal Server Error: {e}")
        return jsonify({'message': 'Internal Server Error', 'details': str(e)}), 500

    # Register MIME types for fonts
    mimetypes.add_type("font/woff", ".woff")
    mimetypes.add_type("font/woff2", ".woff2")
    mimetypes.add_type("font/ttf", ".ttf")
    
    @app.route('/static/fonts/<path:filename>')
    def custom_serve_fonts(filename):
        if filename.endswith('.woff'):
            mimetype = 'font/woff'
        elif filename.endswith('.woff2'):
            mimetype = 'font/woff2'
        elif filename.endswith('.ttf'):
            mimetype = 'font/ttf'
        elif filename.endswith('.otf'):
            mimetype = 'font/otf'
        elif filename.endswith('.eot'):
            mimetype = 'application/vnd.ms-fontobject'
        else:
            mimetype = mimetypes.guess_type(filename)[0]
        return send_from_directory(app.static_folder + '/fonts', filename, mimetype=mimetype)

    # Register blueprints
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_key_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(core_bp)

    return app

def create_admin(app, username, password):
    """
    Creates a new super admin user.
    """
    with app.app_context():
        from scripts.models import User
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin = User(username=username, email=None, password_hash=hashed_password, is_admin=True, is_super_admin=True, hidden=True)
        db.session.add(admin)
        db.session.commit()
        print(f"Super Admin user with username {username} created successfully.")

def recalculate_all_challenge_stripes(app):
    """
    Recalculates and updates the stripe status for all challenges.
    """
    with app.app_context():
        from scripts.models import Challenge
        print("Recalculating stripe statuses for all challenges...")
        challenges = Challenge.query.all()
        for challenge in challenges:
            challenge.update_stripe_status()
            print(f"Updated stripe status for Challenge: {challenge.name}")
        print("All challenge stripe statuses recalculated successfully.")

if __name__ == '__main__':
    from scripts.import_export import import_challenges_from_yaml, import_categories_from_yaml, import_users_from_json, export_data_to_yaml
    parser = argparse.ArgumentParser(description='WindFlag CTF Platform', add_help=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    parser.add_argument('-admin', nargs=2, metavar=('USERNAME', 'PASSWORD'), help='Create an admin user')
    parser.add_argument('-admin-r', type=str, metavar='USERNAME', help='Remove a super admin user.')
    parser.add_argument('-yaml', '-y', type=str, metavar='YAML_FILE', help='Import challenges from a YAML file.')
    parser.add_argument('-users', '-u', type=str, metavar='JSON_FILE', help='Import users from a JSON file.')
    parser.add_argument('-export-yaml', '-e', nargs='+', metavar=('OUTPUT_FILE', 'DATA_TYPE'), help='Export data to a YAML file.')
    parser.add_argument('-recalculate-stripes', action='store_true', help='Recalculate stripe statuses.')
    parser.add_argument('-test', nargs='?', type=int, const=1800, help='Run in test mode.')
    args = parser.parse_args()

    if args.test is not None or '-playwright' in sys.argv:
        from scripts.config import TestConfig
        app = create_app(config_class=TestConfig)
        test_mode_timeout = 360 if '-playwright' in sys.argv else args.test
    else:
        app = create_app()
        test_mode_timeout = None

    if args.admin:
        create_admin(app, args.admin[0], args.admin[1])
    elif args.admin_r:
        with app.app_context():
            from scripts.models import User
            user_to_remove = User.query.filter_by(username=args.admin_r).first()
            if user_to_remove and user_to_remove.is_super_admin:
                db.session.delete(user_to_remove)
                db.session.commit()
                print(f"Super Admin user {args.admin_r} removed successfully.")
            else:
                print(f"Error: User {args.admin_r} not found or not a Super Admin.")
    elif args.yaml:
        import_categories_from_yaml(app, args.yaml)
        import_challenges_from_yaml(app, args.yaml)
    elif args.users:
        import_users_from_json(args.users)
    elif args.export_yaml:
        output_file = args.export_yaml[0]
        data_type = args.export_yaml[1] if len(args.export_yaml) > 1 else 'all'
        export_data_to_yaml(output_file, data_type)
    elif args.recalculate_stripes:
        recalculate_all_challenge_stripes(app)
    else:
        if args.test is not None:
            timer = threading.Timer(test_mode_timeout, os._exit, args=[0])
            timer.start()
        app.run(debug=True, host='0.0.0.0', port=5000)