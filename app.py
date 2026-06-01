import streamlit as st
import requests

WEB_APP_URL = "วาง URL ที่ได้จาก Web App ตรงนี้"

st.set_page_config(page_title="Shark Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์")

# ดึงข้อมูล
response = requests.get(WEB_APP_URL)
data = response.json() # data[0] คือหัวตาราง, data[1:] คือชื่อหมอ
doctors = data[1:] 

# ระบบรันคิว (แบบง่าย)
if 'runner' not in st.session_state: st.session_state.runner = None
with st.sidebar:
    if not st.session_state.runner:
        st.session_state.runner = st.text_input("ใส่ชื่อคนรันคิว:")
    else:
        st.success(f"ผู้รันคิว: {st.session_state.runner}")
        if st.button("ออกจากระบบ"): st.session_state.runner = None; st.rerun()

is_auth = st.session_state.runner is not None

# แสดงผล
for i, row in enumerate(doctors):
    idx = i + 2 # row ใน sheet
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 3, 1])
        col1.write(f"**{row[0]}**")
        
        new_status = col2.selectbox("สถานะ", ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"], 
                                     index=["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"].index(row[1]),
                                     key=f"s_{idx}", disabled=not is_auth)
        
        if new_status != row[1] and is_auth:
            requests.post(WEB_APP_URL, json={"action": "update", "row": idx, "status": new_status})
            st.rerun()
            
        if col3.button("ลบ", key=f"d_{idx}", disabled=not is_auth):
            requests.post(WEB_APP_URL, json={"action": "delete", "row": idx})
            st.rerun()

if is_auth:
    new_name = st.text_input("เพิ่มชื่อ:")
    if st.button("ตกลง"):
        requests.post(WEB_APP_URL, json={"action": "add", "name": new_name})
        st.rerun()
