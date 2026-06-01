import streamlit as st
import requests
import uuid

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

WEBHOOK_URL = "https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux"
STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""

def update_status(doctor_id):
    new_val = st.session_state[f"s_{doctor_id}"]
    if new_val == "⏳ คิวต่อไป":
        for doc in st.session_state.doctors:
            if doc['id'] != doctor_id and doc['status'] == "⏳ คิวต่อไป":
                doc['status'] = "✅ พร้อม"
    for doc in st.session_state.doctors:
        if doc['id'] == doctor_id:
            doc['status'] = new_val
            break

# --- ส่วน Sidebar ---
with st.sidebar:
    st.subheader("⚙️ ตั้งค่ารันคิว")
    if not st.session_state.runner_name:
        runner_input = st.text_input("ชื่อของคุณ:")
        if st.button("ยืนยันตัวตน"):
            st.session_state.runner_name = runner_input
            st.rerun()
    else:
        st.success(f"👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}")
        if st.button("ออกจากระบบ"):
            st.session_state.runner_name = ""
            st.rerun()

# --- เพิ่มรายชื่อ ---
new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ") and new_name:
    st.session_state.doctors.append({"id": str(uuid.uuid4()), "name": new_name, "status": "✅ พร้อม"})
    st.rerun()

st.markdown("---")

# --- ตารางแสดงผล ---
cols = st.columns([1, 4, 3, 2, 1])
cols[0].write("**No.**"); cols[1].write("**ชื่อแพทย์**"); cols[2].write("**สถานะ**"); cols[3].write("**ลำดับ**"); cols[4].write("**ลบ**")

for i, doc in enumerate(st.session_state.doctors):
    c1, c2, c3, c4, c5 = st.columns([1, 4, 3, 2, 1])
    c1.write(f"{i+1}")
    
    # แก้ไขชื่อได้เลย
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    
    c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), key=f"s_{doc['id']}", label_visibility="collapsed", on_change=update_status, args=(doc['id'],))
    
    # ปุ่มเลื่อนลำดับ
    move_up = c4.button("🔼", key=f"up_{doc['id']}")
    move_down = c4.button("🔽", key=f"dn_{doc['id']}")
    if move_up and i > 0:
        st.session_state.doctors[i], st.session_state.doctors[i-1] = st.session_state.doctors[i-1], st.session_state.doctors[i]
        st.rerun()
    if move_down and i < len(st.session_state.doctors) - 1:
        st.session_state.doctors[i], st.session_state.doctors[i+1] = st.session_state.doctors[i+1], st.session_state.doctors[i]
        st.rerun()
        
    if c5.button("🗑️", key=f"d_{doc['id']}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# --- ส่วนส่งข้อมูลไป Discord ---
st.markdown("---")
if st.button("🚀 ส่งข้อมูลไป Discord"):
    # ... (ส่วนเดิมของคุณที่ใช้ทำ message string) ...
    queue_count = sum(1 for d in st.session_state.doctors if d['status'] == "⏳ คิวต่อไป")
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
    elif queue_count > 1:
        st.error(f"❌ ผิดพลาด! มีคนเป็น 'คิวต่อไป' {queue_count} คน")
    else:
        message = f"🚑 **สถานะทีมแพทย์ Shark Community**\n
http://googleusercontent.com/immersive_entry_chip/0

### คำแนะนำเพิ่มเติม:
* การใช้ `st.text_input` ในตารางแบบนี้ช่วยให้คุณแก้ไขข้อมูลได้ทันที (Inline Editing) ซึ่งจะลดขั้นตอนการกดเข้าเมนูย่อยครับ
* หากรายชื่อเริ่มยาวมาก คุณอาจพิจารณาการเก็บข้อมูลลงในไฟล์ `json` หรือ `sqlite` เพื่อไม่ให้ข้อมูลหายเมื่อหน้าเว็บ Refresh (เนื่องจาก `session_state` จะหายไปเมื่อปิด Browser ครับ)
