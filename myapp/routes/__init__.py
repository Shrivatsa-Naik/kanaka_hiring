from .auth import bp as auth_bp
from .hr import bp as hr_bp
from .admin import bp as admin_bp
from .interviewer import bp as interviewer_bp
from .referrer import bp as referrer_bp
from .main import bp as main_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(interviewer_bp)
    app.register_blueprint(referrer_bp)