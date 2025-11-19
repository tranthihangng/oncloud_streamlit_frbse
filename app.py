import streamlit as st
import requests
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
        database_url = st.secrets["firebase"]["database_url"]
    else:
        raise KeyError("No secrets found")
except (KeyError, AttributeError):
    # Fallback về config mặc định
    database_url = "https://cambienanh-sang-default-rtdb.firebaseio.com"

# Firebase Realtime Database URL
FIREBASE_DB_URL = database_url.rstrip('/')

# Tiêu đề
st.title("📊 Dashboard – Light Sensor")
st.markdown("Dữ liệu lấy trực tiếp từ Firebase Realtime Database")

# Sidebar để cấu hình
with st.sidebar:
    st.header("⚙️ Cài đặt")
    auto_refresh = st.checkbox("Tự động làm mới", value=True)
    refresh_interval = st.slider("Khoảng thời gian làm mới (giây)", 1, 60, 5)
    max_data_points = st.slider("Số điểm dữ liệu tối đa", 10, 500, 100)

# Hàm lấy dữ liệu từ Firebase bằng REST API
@st.cache_data(ttl=1)  # Cache 1 giây
def get_sensor_data():
    try:
        # Gọi Firebase Realtime Database REST API
        url = f"{FIREBASE_DB_URL}/sensor_data.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data:
            records = []
            for timestamp, values in data.items():
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
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối Firebase: {e}")
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

