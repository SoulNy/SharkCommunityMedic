import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Dashboard", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# 1. จัดการข้อมูล
if 'doctors' not in st.session_state:
    st.session_state.doctors = []

# ส่วนใส่ Webhook
webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux")

# ส่วนเพิ่มรายชื่อ
with st.form("add_doc_form", clear_on_submit=True):
    new_name = st.text_input("เพิ่มชื่อหมอ:")
    if st.form_submit_button("เพิ่มชื่อ"):
        if new_name:
            st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
            st.rerun()

# ฟังก์ชันจัดการคิว
def update_status(changed_index, new_val):
    # ถ้าเลือก คิวต่อไป ให้เปลี่ยนคนอื่นที่เคยเป็น คิวต่อไป กลับเป็น พร้อม
    if new_val == "⏳ คิวต่อไป":
        for i, doc in enumerate(st.session_state.doctors):
            if i != changed_index and doc['status'] == "⏳ คิวต่อไป":
                doc['status'] = "✅ พร้อม"
    
    st.session_state.doctors[changed_index]['status'] = new_val
    st.rerun()

# 2. แสดงรายการเรียงในแถวเดียว (ใช้ Container เพื่อความสวยงาม)
st.subheader("รายชื่อแพทย์")
for i, doc in enumerate(st.session_state.doctors):
    with st.container(border=True): # สร้างกรอบล้อมรอบแต่ละคน
        cols = st.columns([1, 4, 4, 1])
        
        cols[0].write(f"**{i+1}.**")
        cols[1].write(f"**{doc['name']}**")
        
        # Selectbox สำหรับสถานะ
        options = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]
        new_status = cols[2].selectbox(
            "สถานะ", options, 
            index=options.index(doc['status']),
            key=f"status_{i}",
            on_change=update_status,
            args=(i, st.session_state[f"status_{i}"]),
            label_visibility="collapsed"
        )
        
        if cols[3].button("ลบ", key=f"del_{i}"):
            st.session_state.doctors.pop(i)
            st.rerun()

# 3. ส่งข้อมูล
if st.button("🚀 ส่งข้อมูลไป Discord"):
    content = "🚑 **สถานะทีมแพทย์ Shark Community**\n```\n"
    content += f"{'No.':<4} {'ชื่อแพทย์':<15} | {'สถานะ':<15}\n"
    content += "-"*40 + "\n"
    for i, doc in enumerate(st.session_state.doctors):
        content += f"{i+1:<4} {doc['name']:<15} | {doc['status']}\n"
    content += "```"
    
    try:
        requests.post(webhook_url, json={"content": content})
        st.success("ส่งข้อมูลเรียบร้อย!")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
