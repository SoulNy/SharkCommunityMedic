import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# จัดการข้อมูลใน Session State
if 'doctors' not in st.session_state:
    st.session_state.doctors = []

# ส่วนใส่ข้อมูล
webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux")
new_name = st.text_input("เพิ่มชื่อหมอ:")

if st.button("เพิ่มชื่อ"):
    if new_name:
        st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})

# แสดงรายชื่อแบบง่ายๆ
st.subheader("รายชื่อแพทย์")
for i, doc in enumerate(st.session_state.doctors):
    col1, col2, col3 = st.columns([3, 3, 1])
    col1.write(f"**{i+1}. {doc['name']}**")
    
    # ใช้ Key ที่คงที่เพื่อป้องกัน Error
    doc['status'] = col2.selectbox("สถานะ", ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"], 
                                   index=["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้"].index(doc['status']), 
                                   key=f"status_{i}")
    
    if col3.button("ลบ", key=f"del_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

if st.button("ส่งข้อมูลไป Discord"):
    content = "🚑 **สถานะทีมแพทย์**\n"
    for doc in st.session_state.doctors:
        content += f"{doc['name']} : {doc['status']}\n"
    requests.post(webhook_url, json={"content": content})
    st.success("ส่งข้อมูลแล้ว!")
