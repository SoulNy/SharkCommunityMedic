import streamlit as st
import requests

# เอา URL ที่ได้จากขั้นตอนที่ 7 มาใส่ตรงนี้
WEB_APP_URL = "https://docs.google.com/spreadsheets/d/1aY6iR68-2tXKvlpeQLrjj9Wh0ireTNDDz3GEGQOKIyU/edit?usp=sharing"

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์")

# ดึงข้อมูลจาก Google Sheet
try:
    response = requests.get(WEB_APP_URL)
    data = response.json()
    doctors = data[1:] # ข้อมูลเริ่มแถว 2
except:
    st.error("เชื่อมต่อ Google Sheet ไม่ได้")
    doctors = []

# ระบบรันคิว
if 'runner' not in st.session_state: st.session_state.runner = None
with st.sidebar:
    if not st.session_state.runner:
        name_input = st.text_input("ชื่อผู้รันคิว:")
        if st.button("ตกลง"): st.session_state.runner = name_input; st.rerun()
    else:
        st.success(f"ผู้รันคิว: {st.session_state.runner}")
        if st.button("ออกจากระบบ"): st.session_state.runner = None; st.rerun()

# แสดงผล
is_auth = st.session_state.runner is not None
for i, row in enumerate(doctors):
    idx = i + 2
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 3, 1])
        col1.write(f"**{row[0]}**")
        
        current_status = col2.selectbox("สถานะ", ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"], 
                                       index=["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"].index(row[1]) if row[1] in ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"] else 0,
                                       key=f"s_{idx}", disabled=not is_auth)
        
        if current_status != row[1] and is_auth:
            requests.post(WEB_APP_URL, json={"action": "update", "row": idx, "status": current_status})
            st.rerun()
            
        if col3.button("ลบ", key=f"d_{idx}", disabled=not is_auth):
            requests.post(WEB_APP_URL, json={"action": "delete", "row": idx})
            st.rerun()

if is_auth:
    new_name = st.text_input("เพิ่มชื่อหมอ:")
    if st.button("ตกลงเพิ่มชื่อ"):
        requests.post(WEB_APP_URL, json={"action": "add", "name": new_name})
        st.rerun()
