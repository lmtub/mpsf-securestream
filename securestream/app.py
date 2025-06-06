from flask import Flask
from auth.routes import auth_bp
from stream.routes import stream_bp
from creator.routes import creator_bp
from admin.routes import admin_bp
import os

def create_app():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATES_PATH = os.path.join(BASE_DIR, "..", "templates")
    app = Flask(__name__, template_folder=TEMPLATES_PATH)
    # Đăng ký các blueprint
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(stream_bp, url_prefix="/stream")
    app.register_blueprint(creator_bp, url_prefix="/creator")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    @app.route("/")
    def home():
        return "✅ MPSF SecureStream server is running!"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)