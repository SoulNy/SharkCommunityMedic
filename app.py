import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# 1. จัดการข้อมูลผ่าน session_state เท่านั้น
if 'doctors' not in st.session_state:
    st.session_state.doctors = []

# ส่วนใส่ Webhook
webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/...")

# ส่วนเพิ่มรายชื่อ
with st.form("add_doc_form", clear_on_submit=True):
    new_name = st.text_input("เพิ่มชื่อหมอ:")
    if st.form_submit_button("เพิ่มชื่อ"):
        if new_name:
            st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
            st.rerun()

# 2. แสดงรายการทั้งหมด (ต้องวนลูปจาก st.session_state.doctors)
st.subheader("รายชื่อแพทย์")
for i, doc in enumerate(st.session_state.doctors):
    col1, col2, col3 = st.columns([2, 2, 1])
    
    col1.write(f"{i+1}. {doc['name']}")
    
    # ดึงค่าสถานะจาก session_state
    doc['status'] = col2.selectbox(
        "สถานะ", 
        ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"], 
        key=f"status_{i}",
        index=["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"].index(doc['status'])
    )
    
    if col3.button("ลบ", key=f"del_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# 3. ส่วนส่งข้อมูล
if st.button("🚀 ส่งข้อมูลไป Discord"):
    content = "🚑 **สถานะทีมแพทย์ Shark Community**\n```\n"
    for i, doc in enumerate(st.session_state.doctors):
        content += f"{i+1}. {doc['name']} : {doc['status']}\n"
    content += "```"
    
    try:
        requests.post(webhook_url, json={"content": content})
        st.success("ส่งข้อมูลเรียบร้อย!")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
