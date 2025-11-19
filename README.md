# 📊 Light Sensor Dashboard

Dashboard hiển thị dữ liệu cảm biến ánh sáng từ Firebase Realtime Database, được xây dựng bằng Streamlit.

## 🚀 Tính năng

- ✅ Hiển thị biểu đồ real-time từ Firebase
- ✅ Tự động làm mới dữ liệu
- ✅ Hiển thị metrics (giá trị hiện tại, trung bình, max, min)
- ✅ Bảng dữ liệu chi tiết
- ✅ Giao diện responsive và đẹp mắt

## 📋 Yêu cầu

- Python 3.10+
- Firebase Realtime Database đã được cấu hình

## 🛠️ Cài đặt

```bash
# Tạo virtual environment
py -3.10 -m venv venv310

# Kích hoạt virtual environment
venv310\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## ▶️ Chạy ứng dụng

```bash
streamlit run app.py
```

## ☁️ Deploy lên Streamlit Cloud

Xem hướng dẫn chi tiết trong file [DEPLOY.md](DEPLOY.md)

## 📁 Cấu trúc dự án

```
.
├── app.py              # Ứng dụng Streamlit chính
├── dashboard.html      # Phiên bản HTML (tùy chọn)
├── requirements.txt    # Dependencies
├── README.md          # File này
└── DEPLOY.md          # Hướng dẫn deploy
```

## ⚙️ Cấu hình Firebase

Firebase config được cấu hình trong `app.py`. Bạn có thể:
- Sử dụng config mặc định (hardcoded)
- Hoặc sử dụng Streamlit Secrets để bảo mật hơn (xem DEPLOY.md)

## 📝 License

MIT

