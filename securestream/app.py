import os
from flask import Flask, redirect, send_from_directory, abort

# Đường dẫn thư mục gốc dự án (mpsf-securestream)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Đường dẫn thư mục chứa app.py (securestream/)
APP_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] APP_DIR: {APP_DIR}")

# Đường dẫn thư mục template
TEMPLATES_PATH = os.path.join(BASE_DIR, "templates")

def create_app():
    app = Flask(__name__, template_folder=TEMPLATES_PATH)

    # Import blueprint sau khi Flask app khởi tạo
    from auth.routes import auth_bp
    from stream.routes import stream_bp
    from creator.routes import creator_bp
    from admin.routes import admin_bp

    # Đăng ký blueprint
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(stream_bp, url_prefix="/stream")
    app.register_blueprint(creator_bp, url_prefix="/creator")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def home():
        return redirect("/auth/login")

    # Route phục vụ file trong storage/encrypted_media cũ (giữ lại nếu cần)
    @app.route("/storage/encrypted_media/<path:filename>")
    def encrypted_media(filename):
        media_dir = os.path.join(BASE_DIR, "storage", "encrypted_media")
        print(f"[DEBUG] Trả file từ: {media_dir}\\{filename}")
        return send_from_directory(media_dir, filename)

    # Route phục vụ file ẩn tên thật, dùng storage_name
    @app.route("/media/<path:filename>")
    def serve_media(filename):
        media_dir = os.path.join(BASE_DIR, "storage", "encrypted_media")
        file_path = os.path.join(media_dir, filename)

        if not os.path.exists(file_path):
            print(f"[LỖI] Không tìm thấy file: {file_path}")
            return abort(404)

        print(f"[DEBUG] Phục vụ file: {file_path}")
        return send_from_directory(media_dir, filename)

    return app

if __name__ == "__main__":
    cert_path = os.path.join(APP_DIR, "cert.pem")
    key_path = os.path.join(APP_DIR, "key.pem")

    app = create_app()
    app.run(ssl_context=(cert_path, key_path))
