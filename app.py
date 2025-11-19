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
    show_debug = st.checkbox("Hiển thị thông tin debug", value=False)

# Hàm lấy dữ liệu từ Firebase bằng REST API
@st.cache_data(ttl=1)  # Cache 1 giây
def get_sensor_data(show_debug=False):
    try:
        # Gọi Firebase Realtime Database REST API
        url = f"{FIREBASE_DB_URL}/sensor_data.json"
        
        if show_debug:
            st.info(f"🔗 Đang kết nối: `{url}`")
        
        response = requests.get(url, timeout=10)
        
        if show_debug:
            st.info(f"📡 Status Code: {response.status_code}")
        
        # Kiểm tra nếu bị từ chối (có thể do Rules)
        if response.status_code == 401 or response.status_code == 403:
            st.error("❌ **Lỗi quyền truy cập**: Firebase Database Rules không cho phép đọc công khai. Vui lòng cập nhật Rules trong Firebase Console.")
            if show_debug:
                st.code(response.text, language="json")
            return pd.DataFrame()
        
        response.raise_for_status()
        
        data = response.json()
        
        if show_debug:
            st.json(data if data else {"message": "Không có dữ liệu"})
        
        if data is None:
            if show_debug:
                st.warning("⚠️ Firebase trả về `null` - Có thể path `sensor_data` không tồn tại hoặc trống")
            return pd.DataFrame()
        
        if not data:
            if show_debug:
                st.warning("⚠️ Firebase trả về object rỗng `{}`")
            return pd.DataFrame()
        
        records = []
        # Xử lý cấu trúc dữ liệu 3 tầng: ngày -> giờ -> dữ liệu
        for date_key, time_data in data.items():
            if isinstance(time_data, dict):
                # Duyệt qua từng thời gian trong ngày
                for time_key, sensor_data in time_data.items():
                    if isinstance(sensor_data, dict) and "light_inte" in sensor_data:
                        # Tạo timestamp từ ngày và giờ
                        try:
                            # Kết hợp ngày và giờ để tạo datetime
                            datetime_str = f"{date_key} {time_key}"
                            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            # Nếu không parse được, dùng format gốc
                            timestamp = f"{date_key} {time_key}"
                            dt = None
                        
                        records.append({
                            "timestamp": timestamp,
                            "light_inte": sensor_data.get("light_inte", 0),
                            "raw": sensor_data.get("raw", 0),
                            "datetime": dt
                        })
                    elif show_debug and isinstance(sensor_data, dict):
                        st.warning(f"⚠️ Không tìm thấy key 'light_inte' trong: {date_key}/{time_key}")
            elif show_debug:
                st.warning(f"⚠️ Giá trị không phải dict: {date_key} = {time_data}")
        
        if records:
            df = pd.DataFrame(records)
            # Sắp xếp theo datetime nếu có, nếu không thì theo timestamp
            if df['datetime'].notna().any():
                df = df.sort_values("datetime").tail(max_data_points)
            else:
                df = df.sort_values("timestamp").tail(max_data_points)
            if show_debug:
                st.success(f"✅ Đã lấy được {len(records)} bản ghi (hiển thị {len(df)} bản ghi)")
            return df
        else:
            if show_debug:
                st.warning("⚠️ Không tìm thấy bản ghi nào có key 'light_inte'")
            return pd.DataFrame()
            
    except requests.exceptions.Timeout:
        st.error("⏱️ **Lỗi timeout**: Không thể kết nối đến Firebase trong thời gian cho phép")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("🌐 **Lỗi kết nối**: Không thể kết nối đến Firebase. Kiểm tra internet và URL database.")
        return pd.DataFrame()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ **Lỗi HTTP {e.response.status_code}**: {e}")
        if show_debug and e.response.text:
            st.code(e.response.text, language="json")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ **Lỗi kết nối Firebase**: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ **Lỗi không xác định**: {e}")
        if show_debug:
            import traceback
            st.code(traceback.format_exc(), language="python")
        return pd.DataFrame()

# Lấy dữ liệu
df = get_sensor_data(show_debug=show_debug)

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
    
    # Sử dụng datetime nếu có, nếu không dùng timestamp
    x_data = df['datetime'] if df['datetime'].notna().any() else df['timestamp']
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=df['light_inte'],
        mode='lines+markers',
        name='Light (%)',
        line=dict(width=2, color='#1f77b4'),
        marker=dict(size=4),
        hovertemplate='<b>Thời gian:</b> %{x}<br><b>Light:</b> %{y}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Biểu đồ Light Sensor",
        xaxis_title="Thời gian",
        yaxis_title="Light (%)",
        height=400,
        hovermode='x unified',
        template='plotly_white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Hiển thị bảng dữ liệu
    with st.expander("📋 Xem dữ liệu chi tiết"):
        display_cols = ['timestamp', 'light_inte']
        if 'raw' in df.columns:
            display_cols.append('raw')
        st.dataframe(df[display_cols].tail(20), use_container_width=True)
    
    # Làm mới tự động
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
else:
    st.warning("⚠️ Chưa có dữ liệu từ Firebase. Vui lòng kiểm tra kết nối và cấu hình.")
    
    # Hiển thị thông tin debug và hướng dẫn
    with st.expander("🔍 Hướng dẫn khắc phục"):
        st.markdown("""
        **Các bước kiểm tra:**
        
        1. **Firebase Database Rules**: Đảm bảo Rules cho phép đọc công khai:
        ```json
        {
          "rules": {
            "sensor_data": {
              ".read": true,
              ".write": false
            }
          }
        }
        ```
        
        2. **Kiểm tra URL Database**: Xem bên dưới
        
        3. **Kiểm tra path dữ liệu**: Đảm bảo có dữ liệu tại path `sensor_data` trong Firebase Console
        
        4. **Cấu trúc dữ liệu**: Dữ liệu phải có dạng (3 tầng: ngày -> giờ -> dữ liệu):
        ```json
        {
          "sensor_data": {
            "2025-11-19": {
              "10:20:59": {
                "light_inte": 39,
                "raw": 2511
              },
              "10:21:09": {
                "light_inte": 39,
                "raw": 2499
              }
            }
          }
        }
        ```
        
        5. **Bật chế độ Debug**: Tích vào checkbox "Hiển thị thông tin debug" ở sidebar để xem chi tiết lỗi
        """)
        st.info(f"**Database URL hiện tại**: `{FIREBASE_DB_URL}`")
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

