# Hướng dẫn chạy Dashboard Streamlit

## Cài đặt

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
streamlit run app.py
```

Ứng dụng sẽ tự động mở trong trình duyệt tại địa chỉ `http://localhost:8501`

## Cấu hình Firebase

1. Mở file `app.py`
2. Cập nhật thông tin Firebase trong biến `firebaseConfig`:
   - `apiKey`: API Key từ Firebase Console
   - `authDomain`: Auth Domain của dự án
   - `databaseURL`: URL của Realtime Database
   - `projectId`: Project ID
   - `storageBucket`: Storage Bucket
   - `messagingSenderId`: Messaging Sender ID
   - `appId`: App ID

## Tính năng

- ✅ Hiển thị biểu đồ real-time từ Firebase
- ✅ Tự động làm mới dữ liệu
- ✅ Hiển thị các metrics (giá trị hiện tại, trung bình, max, min)
- ✅ Bảng dữ liệu chi tiết
- ✅ Giao diện responsive và đẹp mắt

## Triển khai lên Streamlit Cloud

1. Đẩy code lên GitHub
2. Truy cập https://streamlit.io/cloud
3. Kết nối repository
4. Deploy ứng dụng

**Lưu ý**: Cần cấu hình Firebase credentials trong Streamlit Secrets nếu deploy lên cloud.

