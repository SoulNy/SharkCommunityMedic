import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")

# --- ข้อมูลหลัก ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = None
if 'webhook_enabled' not in st.session_state: st.session_state.webhook_enabled = True

# --- ปุ่มรันคิว (ขวาบน) ---
col_top1, col_top2 = st.columns([4, 1])
with col_top2:
    if st.button("🔑 เริ่มรันคิว"):
        new_name = st.text_input("ชื่อผู้รันคิว:", key="run_input")
        if st.button("ตกลง"):
            st.session_state.runner_name = new_name
            st.rerun()

# แสดงชื่อคนรันคิว
if st.session_state.runner_name:
    st.info(f"👨‍⚕️ ผู้รันคิวปัจจุบัน: {st.session_state.runner_name}")

st.title("🚑 ระบบจัดการสถานะแพทย์")

# ตั้งค่า Webhook
st.session_state.webhook_enabled = st.toggle("เปิดใช้งาน Webhook", value=st.session_state.webhook_enabled)
webhook_url = st.text_input("Webhook URL:", value="...")

# --- ระบบแก้ไข (เช็คสิทธิ์) ---
is_authorized = st.session_state.runner_name is not None

with st.form("add_doc_form", clear_on_submit=True):
    new_name = st.text_input("เพิ่มชื่อหมอ (เฉพาะผู้รันคิว):", disabled=not is_authorized)
    if st.form_submit_button("เพิ่มชื่อ"):
        if is_authorized and new_name:
            st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
            st.rerun()

# --- แสดงรายชื่อ ---
for i, doc in enumerate(st.session_state.doctors):
    with st.container(border=True):
        cols = st.columns([1, 4, 4, 1])
        cols[0].write(f"{i+1}.")
        cols[1].write(doc['name'])
        
        # ปิดการแก้ไขถ้าไม่ได้รันคิว
        new_status = cols[2].selectbox(
            "สถานะ", ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"],
            index=["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"].index(doc['status']),
            key=f"status_{i}",
            disabled=not is_authorized,
            label_visibility="collapsed"
        )
        st.session_state.doctors[i]['status'] = new_status
        
        if cols[3].button("ลบ", key=f"del_{i}", disabled=not is_authorized):
            st.session_state.doctors.pop(i)
            st.rerun()

# --- ส่งข้อมูล ---
if st.button("🚀 ส่งข้อมูลไป Discord"):
    if not st.session_state.webhook_enabled:
        st.warning("Webhook ปิดอยู่ครับ")
    elif is_authorized:
        # (ใส่โค้ด requests.post ตามเดิม)
        st.success("ส่งข้อมูลเรียบร้อย!")
    else:
        st.error("ต้องเป็นผู้รันคิวถึงจะส่งได้!")
