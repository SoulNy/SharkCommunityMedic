import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

if 'doctors' not in st.session_state:
    st.session_state.doctors = []

webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux")

# ฟังก์ชันอัปเดตแบบเคลียร์คิวเก่าให้คนใหม่เสมอ
def update_status_callback(changed_index):
    new_val = st.session_state[f"status_{changed_index}"]
    
    # ถ้ามีการกด "คิวต่อไป" ให้คนอื่นทุกคนกลายเป็น "พร้อม" ทันที
    if new_val == "⏳ คิวต่อไป":
        for i in range(len(st.session_state.doctors)):
            if i != changed_index:
                st.session_state[f"status_{i}"] = "✅ พร้อม"
                st.session_state.doctors[i]['status'] = "✅ พร้อม"
    
    # อัปเดตคนที่กด
    st.session_state.doctors[changed_index]['status'] = new_val

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
        
        # เมื่อเปลี่ยนค่า ให้เรียก callback
        cols[2].selectbox(
            "สถานะ", options, 
            index=options.index(doc['status']),
            key=f"status_{i}",
            on_change=update_status_callback,
            args=(i,),
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
