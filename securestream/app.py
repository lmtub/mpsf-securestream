from flask import Flask
from auth.routes import auth_bp
from stream.routes import stream_bp

def create_app():
    app = Flask(__name__)

    # Đăng ký các blueprint
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(stream_bp, url_prefix="/stream")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

@app.route("/")
def home():
    return "✅ MPSF SecureStream server is running!"