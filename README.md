
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

## ⚙️ Cài đặt và chạy thử

### Bước 1: Chuẩn bị môi trường

- Yêu cầu:
  - Python 3.10+
  - FFmpeg (đã cài và cấu hình PATH)
  - Shaka Packager (đã cài và cấu hình PATH)

---

### Bước 2: Cài đặt FFmpeg

**Cách 1:** Truy cập [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)  
Tải bản:  
✔️ `ffmpeg-release-full.zip` hoặc `ffmpeg-release-full.7z`  

Giải nén vào `C:\ffmpeg`  
Thêm `C:\ffmpeg\bin` vào biến môi trường `PATH`

**Cách 2:** Dùng Winget trên PowerShell:

```powershell
winget install ffmpeg
```

Hoặc bản đầy đủ:

```powershell
winget install "FFmpeg (Essentials Build)"
```

Kiểm tra:

```powershell
ffmpeg -version
```

---

### Bước 3: Cài đặt Shaka Packager

- Tải từ: [https://github.com/shaka-project/shaka-packager/releases](https://github.com/shaka-project/shaka-packager/releases)  

Đổi tên và di chuyển:

```powershell
Rename-Item .\packager-win-x64.exe packager.exe
Move-Item .\packager.exe C:\ffmpeg\bin
```

Kiểm tra:

```powershell
packager --version
```

---

### Bước 4: Cài đặt và chạy dự án SecureStream

```bash
git clone https://github.com/lmtub/mpsf-securestream.git
cd mpsf-securestream
pip install -r requirements.txt
python -m securestream.app
```

Truy cập hệ thống tại: [http://localhost:5000](http://localhost:5000)  

---

### ✅ Kiểm tra nhanh

- Phát nội dung thử nghiệm trên trình duyệt.
- Quan sát console log: `"Phát thành công"`.
- Backend chỉ cấp key hợp lệ khi người dùng đủ quyền.

---
