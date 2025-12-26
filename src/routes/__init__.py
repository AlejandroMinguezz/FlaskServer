from .auth import bp as auth_bp
from .files import bp as files_bp
from .metadata import bp as metadata_bp
from .health import bp as health_bp
from .file_icons_route import bp as file_icons_bp
from .folder_structure import bp as folder_structure_bp
from .ia import bp as ia_bp
from .feedback import bp as feedback_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(metadata_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(file_icons_bp)
    app.register_blueprint(folder_structure_bp)
    app.register_blueprint(ia_bp)
    app.register_blueprint(feedback_bp)
