# SecureStream - Multimedia Secure Streaming Platform

🚀 **SecureStream** là mô hình mô phỏng nền tảng phát nội dung số có bản quyền (phim, nhạc) với cơ chế bảo vệ toàn diện, kết hợp mã hóa hiện đại, DRM, và phân quyền người dùng.

---
## Danh sách thành viên thực hiện

| STT | MSSV     | Họ và tên            |
|-----|----------|----------------------|
| 1   | 23521398 | Lê Minh Tấn          |
| 2   | 23521433 | Trần Viết Thắng      |
| 3   | 23521425 | Nguyễn Quang Thắng   |
---

## 🌐 **Tính năng nổi bật**

- Mã hóa nội dung với **AES-256-GCM** kết hợp **Chaotic Stream Cipher** tăng tính ngẫu nhiên.
- Đóng gói nội dung chuẩn **DASH + Widevine DRM**, hỗ trợ phát trực tuyến an toàn.
- Phân quyền người dùng rõ ràng: `user`, `creator`, `admin`.
- Bảo vệ truy cập thông qua **JWT** và các route kiểm soát nội dung (`/media/...`).
- Tích hợp **Shaka Player** hỗ trợ phát nội dung chỉ khi được cấp key hợp lệ.
- Mô phỏng cấp key qua API backend, có thể nâng cấp thành License Server tách biệt.

---

## 🛠️ **Công nghệ sử dụng**

- **Python 3.10+**, Flask Framework
- **PyCryptodome** (AES-256-GCM)
- **NumPy** (Chaotic stream generation)
- **JWT (JSON Web Token)** cho xác thực và phân quyền
- **Shaka Player** (Frontend) hỗ trợ EME/CDM
- **Shaka Packager** đóng gói nội dung DASH + Widevine DRM
- **FFmpeg** chuẩn hóa đầu vào video/audio

---

## ⚙️ **Cài đặt và chạy thử**

```bash
git clone https://github.com/lmtub/mpsf-securestream.git
cd securestream
pip install -r requirements.txt
python -m securestream.app
