import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# สถานะทั้งหมด
STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""

# Sidebar สำหรับคนรันคิว
with st.sidebar:
    st.subheader("⚙️ ตั้งค่ารันคิว")
    if not st.session_state.runner_name:
        runner_input = st.text_input("ใส่ชื่อผู้รันคิวของคุณ:")
        if st.button("ยืนยันตัวตน"):
            st.session_state.runner_name = runner_input
            st.rerun()
    else:
        st.success(f"👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}")
        if st.button("ออกจากระบบ"):
            st.session_state.runner_name = ""
            st.rerun()

webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux")
new_name = st.text_input("เพิ่มชื่อหมอ:")

if st.button("เพิ่มชื่อ"):
    if not st.session_state.runner_name:
        st.error("กรุณายืนยันชื่อผู้รันคิวในเมนูด้านซ้ายก่อน!")
    elif new_name:
        st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
        st.rerun()

st.subheader("รายชื่อแพทย์")
for i, doc in enumerate(st.session_state.doctors):
    col_name, col_status, col_del = st.columns([3, 3, 1])
    col_name.write(f"**{i+1}. {doc['name']}**")
    
    old_status = doc['status']
    new_status = col_status.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(old_status), key=f"s_{i}", label_visibility="collapsed")
    
    # Logic: ถ้าเลือก "คิวต่อไป" ให้คนอื่นเป็น "พร้อม"
    if new_status != old_status:
        if new_status == "⏳ คิวต่อไป":
            for j, d in enumerate(st.session_state.doctors):
                if i != j and d['status'] == "⏳ คิวต่อไป":
                    st.session_state.doctors[j]['status'] = "✅ พร้อม"
        
        doc['status'] = new_status
        st.rerun()
    
    if col_del.button("ลบ", key=f"d_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

if st.button("🚀 ส่งข้อมูลไป Discord"):
    if not st.session_state.runner_name:
        st.error("ต้องมีชื่อผู้รันคิวก่อนถึงจะส่งได้ครับ!")
    else:
        content = f"🚑 **สถานะทีมแพทย์ (อัปเดตโดย: {st.session_state.runner_name})**\n```\n"
        for doc in st.session_state.doctors:
            content += f"{doc['name']} : {doc['status']}\n"
        content += "```"
        requests.post(webhook_url, json={"content": content})
        st.success("ส่งข้อมูลไป Discord เรียบร้อย!")
