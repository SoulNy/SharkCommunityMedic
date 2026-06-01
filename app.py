import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

WEBHOOK_URL = "ใส่_WEBHOOK_URL_ของคุณที่นี่"
STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""

# --- Callback Function สำหรับจัดการคิว ---
def update_status(index, new_val):
    if new_val == "⏳ คิวต่อไป":
        # เปลี่ยนคนอื่นที่เคยเป็น "คิวต่อไป" ให้เป็น "พร้อม"
        for i in range(len(st.session_state.doctors)):
            if i != index and st.session_state.doctors[i]['status'] == "⏳ คิวต่อไป":
                st.session_state.doctors[i]['status'] = "✅ พร้อม"
    
    # อัปเดตสถานะของคนที่เลือก
    st.session_state.doctors[index]['status'] = new_val

# --- ส่วน UI ---
with st.sidebar:
    st.subheader("⚙️ ตั้งค่ารันคิว")
    if not st.session_state.runner_name:
        if st.button("ยืนยันตัวตน"): st.session_state.runner_name = st.text_input("ชื่อของคุณ:")
    else:
        st.success(f"👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}")
        if st.button("ออกจากระบบ"): st.session_state.runner_name = ""

new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ") and new_name:
    st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
    st.rerun()

st.markdown("---")

# --- ตารางแสดงผล ---
head1, head2, head3, head4 = st.columns([1, 4, 3, 1])
head1.write("**No.**"); head2.write("**ชื่อแพทย์**"); head3.write("**สถานะ**"); head4.write("**จัดการ**")

for i, doc in enumerate(st.session_state.doctors):
    col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
    col1.write(f"{i+1}")
    col2.write(f"{doc['name']}")
    
    # ใช้ on_change เพื่อบังคับให้ Logic ทำงานทันทีที่เปลี่ยนค่า
    col3.selectbox(
        "สถานะ", 
        STATUS_OPTIONS, 
        index=STATUS_OPTIONS.index(doc['status']), 
        key=f"s_{i}", 
        label_visibility="collapsed",
        on_change=update_status,
        args=(i, st.session_state[f"s_{i}"]) 
    )
    
    if col4.button("ลบ", key=f"d_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# --- ส่วนส่ง Discord ---
st.markdown("---")
if st.button("🚀 ส่งข้อมูลไป Discord"):
    # ตรวจสอบความถูกต้องก่อนส่ง
    queue_count = sum(1 for d in st.session_state.doctors if d['status'] == "⏳ คิวต่อไป")
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
    elif queue_count > 1:
        st.error("❌ ผิดพลาด! มีคนเป็น 'คิวต่อไป' มากกว่า 1 คน")
    else:
        message = f"🚑 **อัปเดตสถานะ - โดย {st.session_state.runner_name}**\n" + "\n".join([f"{d['status']} {d['name']}" for d in st.session_state.doctors])
        try:
            requests.post(WEBHOOK_URL, json={"content": message})
            st.success("✅ ส่งข้อมูลไป Discord แล้ว!")
        except Exception as e:
            st.error(f"Error: {e}")
