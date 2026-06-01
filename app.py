import streamlit as st
import requests

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# จัดการ Webhook (ใช้ session_state เพื่อจำค่า)
if 'webhook_url' not in st.session_state:
    st.session_state.webhook_url = "ใส่ URL ของคุณที่นี่"

st.session_state.webhook_url = st.text_input("Webhook URL:", value=st.session_state.webhook_url)

# รายชื่อ (สมมติว่าเป็น List)
if 'doctors' not in st.session_state:
    st.session_state.doctors = []

# เพิ่มชื่อ
new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ"):
    st.session_state.doctors.append({"name": new_name, "status": "พร้อม"})

# แสดงรายการ
for i, doc in enumerate(st.session_state.doctors):
    col1, col2, col3 = st.columns([2, 2, 1])
    col1.write(f"{i+1}. {doc['name']}")
    doc['status'] = col2.selectbox("สถานะ", ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"], key=f"status_{i}")
    if col3.button("ลบ", key=f"del_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# ส่งข้อมูล
if st.button("🚀 ส่งข้อมูลไป Discord"):
    # เขียน logic การสร้างข้อความและยิง requests.post เหมือนเดิมครับ
    st.success("ส่งข้อมูลเรียบร้อย!")