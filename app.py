import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

if 'doctors' not in st.session_state:
    st.session_state.doctors = []

webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux")

# ฟังก์ชันจัดการคิวแบบปลอดภัย
def update_status_callback():
    # ตรวจสอบว่าอันไหนคือตัวที่ถูกกดเปลี่ยน
    for i in range(len(st.session_state.doctors)):
        key = f"status_{i}"
        if key in st.session_state:
            new_val = st.session_state[key]
            # ถ้าเลือก "คิวต่อไป" ให้ล้างคนอื่น
            if new_val == "⏳ คิวต่อไป":
                for j in range(len(st.session_state.doctors)):
                    if i != j:
                        st.session_state[f"status_{j}"] = "✅ พร้อม"
                        st.session_state.doctors[j]['status'] = "✅ พร้อม"
            st.session_state.doctors[i]['status'] = new_val

with st.form("add_doc_form", clear_on_submit=True):
    new_name = st.text_input("เพิ่มชื่อหมอ:")
    if st.form_submit_button("เพิ่มชื่อ"):
        if new_name:
            st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
            st.rerun()

st.subheader("รายชื่อแพทย์")
for i, doc in enumerate(st.session_state.doctors):
    with st.container(border=True):
        cols = st.columns([1, 4, 4, 1])
        cols[0].write(f"**{i+1}.**")
        cols[1].write(f"**{doc['name']}**")
        
        options = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]
        
        # ปรับการเรียกใช้ key ให้ถูกต้อง
        cols[2].selectbox(
            "สถานะ", options, 
            index=options.index(doc['status']),
            key=f"status_{i}",
            on_change=update_status_callback, # เรียกฟังก์ชันอัปเดต
            label_visibility="collapsed"
        )
        
        if cols[3].button("ลบ", key=f"del_{i}"):
            st.session_state.doctors.pop(i)
            st.rerun()

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
