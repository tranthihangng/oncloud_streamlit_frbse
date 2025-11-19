import streamlit as st
import pyrebase
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Cấu hình trang
st.set_page_config(
    page_title="Light Sensor Dashboard",
    page_icon="📊",
    layout="wide"
)

# Firebase config - Đọc từ Streamlit Secrets nếu có, nếu không dùng config mặc định
try:
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
    else:
        raise KeyError("No secrets found")
except (KeyError, AttributeError):
    # Fallback về config mặc định
    firebaseConfig = {
        "apiKey": "AIzaSyAzOaM9SoQcYi7aAAF5kwEXN-DMB-6gDkY",
        "authDomain": "cambienanh-sang.firebaseapp.com",
        "databaseURL": "https://cambienanh-sang-default-rtdb.firebaseio.com",
        "projectId": "cambienanh-sang",
        "storageBucket": "cambienanh-sang.firebasestorage.app",
        "messagingSenderId": "1086585961238",
        "appId": "1:1086585961238:web:70ac5ddcb7cb817e3c2e37"
    }

# Khởi tạo Firebase
try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    db = firebase.database()
except Exception as e:
    st.error(f"Lỗi kết nối Firebase: {e}")
    st.stop()

# Tiêu đề
st.title("📊 Dashboard – Light Sensor")
st.markdown("Dữ liệu lấy trực tiếp từ Firebase Realtime Database")

# Sidebar để cấu hình
with st.sidebar:
    st.header("⚙️ Cài đặt")
    auto_refresh = st.checkbox("Tự động làm mới", value=True)
    refresh_interval = st.slider("Khoảng thời gian làm mới (giây)", 1, 60, 5)
    max_data_points = st.slider("Số điểm dữ liệu tối đa", 10, 500, 100)

# Hàm lấy dữ liệu từ Firebase
@st.cache_data(ttl=1)  # Cache 1 giây
def get_sensor_data():
    try:
        data = db.child("sensor_data").get()
        if data.val():
            records = []
            for timestamp, values in data.val().items():
                if isinstance(values, dict) and "light_inte" in values:
                    records.append({
                        "timestamp": timestamp,
                        "light_inte": values.get("light_inte", 0),
                        "datetime": datetime.fromtimestamp(int(timestamp)) if timestamp.isdigit() else None
                    })
            
            if records:
                df = pd.DataFrame(records)
                # Sắp xếp theo timestamp và giới hạn số điểm
                df = df.sort_values("timestamp").tail(max_data_points)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi khi lấy dữ liệu: {e}")
        return pd.DataFrame()

# Lấy dữ liệu
df = get_sensor_data()

# Hiển thị metrics
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Giá trị hiện tại", f"{df['light_inte'].iloc[-1]:.1f}%")
    
    with col2:
        st.metric("Giá trị trung bình", f"{df['light_inte'].mean():.1f}%")
    
    with col3:
        st.metric("Giá trị tối đa", f"{df['light_inte'].max():.1f}%")
    
    with col4:
        st.metric("Giá trị tối thiểu", f"{df['light_inte'].min():.1f}%")
    
    # Vẽ biểu đồ
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'] if df['datetime'].isna().all() else df['datetime'],
        y=df['light_inte'],
        mode='lines+markers',
        name='Light (%)',
        line=dict(width=2, color='#1f77b4'),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title="Biểu đồ Light Sensor",
        xaxis_title="Thời gian",
        yaxis_title="Light (%)",
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Hiển thị bảng dữ liệu
    with st.expander("📋 Xem dữ liệu chi tiết"):
        st.dataframe(df[['timestamp', 'light_inte']].tail(20), use_container_width=True)
    
    # Làm mới tự động
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
else:
    st.warning("⚠️ Chưa có dữ liệu từ Firebase. Vui lòng kiểm tra kết nối và cấu hình.")
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

