# Hướng dẫn Deploy lên Streamlit Cloud

## Bước 1: Chuẩn bị Repository GitHub

1. **Khởi tạo Git repository** (nếu chưa có):
```bash
cd d:\anh_sang
git init
git add .
git commit -m "Initial commit: Streamlit Light Sensor Dashboard"
```

2. **Tạo repository trên GitHub**:
   - Truy cập https://github.com/new
   - Tạo repository mới (ví dụ: `light-sensor-dashboard`)
   - **KHÔNG** tích vào "Initialize with README"

3. **Push code lên GitHub**:
```bash
git remote add origin https://github.com/YOUR_USERNAME/light-sensor-dashboard.git
git branch -M main
git push -u origin main
```

## Bước 2: Deploy lên Streamlit Cloud

1. **Truy cập Streamlit Cloud**:
   - Đi tới https://share.streamlit.io/
   - Đăng nhập bằng tài khoản GitHub

2. **Deploy ứng dụng**:
   - Click nút "New app"
   - Chọn repository: `YOUR_USERNAME/light-sensor-dashboard`
   - Chọn branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

## Bước 3: Cấu hình Secrets (Tùy chọn - Nếu muốn ẩn Firebase config)

Nếu bạn muốn bảo mật thông tin Firebase, có thể sử dụng Streamlit Secrets:

1. **Trong Streamlit Cloud**:
   - Vào app settings → Secrets
   - Thêm các biến sau:
```toml
[firebase]
api_key = "AIzaSyAzOaM9SoQcYi7aAAF5kwEXN-DMB-6gDkY"
auth_domain = "cambienanh-sang.firebaseapp.com"
database_url = "https://cambienanh-sang-default-rtdb.firebaseio.com"
project_id = "cambienanh-sang"
storage_bucket = "cambienanh-sang.firebasestorage.app"
messaging_sender_id = "1086585961238"
app_id = "1:1086585961238:web:70ac5ddcb7cb817e3c2e37"
```

2. **Cập nhật app.py để đọc từ secrets** (tùy chọn):
```python
# Thay vì hardcode, có thể dùng:
if 'firebase' in st.secrets:
    firebaseConfig = {
        "apiKey": st.secrets["firebase"]["api_key"],
        "authDomain": st.secrets["firebase"]["auth_domain"],
        "databaseURL": st.secrets["firebase"]["database_url"],
        "projectId": st.secrets["firebase"]["project_id"],
        "storageBucket": st.secrets["firebase"]["storage_bucket"],
        "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
        "appId": st.secrets["firebase"]["app_id"]
    }
```

## Lưu ý quan trọng

1. **Firebase Rules**: Đảm bảo Firebase Realtime Database Rules cho phép đọc công khai hoặc cấu hình authentication phù hợp

2. **CORS**: Firebase Realtime Database cần được cấu hình để cho phép truy cập từ domain Streamlit Cloud

3. **URL ứng dụng**: Sau khi deploy, bạn sẽ có URL dạng:
   `https://YOUR_APP_NAME.streamlit.app`

## Troubleshooting

- **Lỗi kết nối Firebase**: Kiểm tra Firebase Rules và CORS settings
- **Lỗi import**: Đảm bảo tất cả dependencies trong `requirements.txt` đã được cài đặt
- **Lỗi secrets**: Nếu dùng secrets, đảm bảo format TOML đúng

