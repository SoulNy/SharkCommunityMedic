import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# --- Initialize Session State ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = None
if 'webhook_enabled' not in st.session_state: st.session_state.webhook_enabled = True

# --- จัดการชื่อผู้รันคิว (แบบที่เสถียรที่สุด) ---
with st.sidebar:
    st.subheader("⚙️ ตั้งค่าระบบ")
    if not st.session_state.runner_name:
        run_name = st.text_input("ใส่ชื่อผู้รันคิว:")
        if st.button("ตกลง"):
            st.session_state.runner_name = run_name
            st.rerun()
    else:
        st.success(f"👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}")
        if st.button("ออกจากระบบรันคิว"):
            st.session_state.runner_name = None
            st.rerun()
    
    st.session_state.webhook_enabled = st.toggle("เปิดใช้งาน Webhook", value=st.session_state.webhook_enabled)
    webhook_url = st.text_input("Webhook URL:", value="ใส่ URL ที่นี่")

# --- ตรวจสอบสิทธิ์ ---
is_authorized = st.session_state.runner_name is not None

# --- ส่วนเพิ่มรายชื่อ ---
new_name = st.text_input("เพิ่มชื่อหมอ:", disabled=not is_authorized)
if st.button("เพิ่มชื่อ") and is_authorized:
    if new_name:
        st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
        st.rerun()

# --- แสดงรายชื่อ ---
st.subheader("รายชื่อแพทย์")
for i, doc in enumerate(st.session_state.doctors):
    with st.container(border=True):
        cols = st.columns([1, 3, 3, 1])
        cols[0].write(f"**{i+1}.**")
        cols[1].write(f"**{doc['name']}**")
        
        options = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"]
        
        # ใส่ disabled=not is_authorized เพื่อให้แก้ได้เฉพาะคนรันคิว
        new_status = cols[2].selectbox(
            "สถานะ", options, 
            index=options.index(doc['status']),
            key=f"status_{i}",
            disabled=not is_authorized,
            label_visibility="collapsed"
        )
        
        if cols[3].button("ลบ", key=f"del_{i}", disabled=not is_authorized):
            st.session_state.doctors.pop(i)
            st.rerun()

# --- ส่งข้อมูล ---
if st.button("🚀 ส่งข้อมูลไป Discord"):
    if not st.session_state.webhook_enabled:
        st.warning("Webhook ปิดอยู่")
    elif not is_authorized:
        st.error("เฉพาะผู้รันคิวเท่านั้นที่กดส่งได้!")
    else:
        content = f"🚑 **สถานะทีมแพทย์โดย {st.session_state.runner_name}**\n```\n"
        for doc in st.session_state.doctors:
            content += f"{doc['name']} : {doc['status']}\n"
        content += "```"
        requests.post(webhook_url, json={"content": content})
        st.success("ส่งข้อมูลเรียบร้อย!")
