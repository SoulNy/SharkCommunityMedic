import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# กำหนดค่าเริ่มต้นใน session_state
if 'doctors' not in st.session_state: 
    st.session_state.doctors = []
if 'runner_name' not in st.session_state: 
    st.session_state.runner_name = ""

# --- Sidebar ---
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

# --- ส่วนเพิ่มรายชื่อ ---
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
    
    # ดึงค่าสถานะปัจจุบัน
    current_status = doc['status']
    
    # เลือกสถานะใหม่
    new_status = col3.selectbox(
        "สถานะ", 
        STATUS_OPTIONS, 
        index=STATUS_OPTIONS.index(current_status), 
        key=f"s_{i}", 
        label_visibility="collapsed"
    )
    
    # Logic: ถ้าเลือก "คิวต่อไป" ให้คนอื่นที่เหลือเป็น "พร้อม" ทันที
    if new_status != current_status:
        if new_status == "⏳ คิวต่อไป":
            for j in range(len(st.session_state.doctors)):
                if j != i and st.session_state.doctors[j]['status'] == "⏳ คิวต่อไป":
                    st.session_state.doctors[j]['status'] = "✅ พร้อม"
        
        doc['status'] = new_status
        st.rerun() # รีโหลดหน้าจอเพื่ออัปเดตข้อมูล
        
    if col4.button("ลบ", key=f"d_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# --- ส่ง Discord ---
st.markdown("---")
if st.button("🚀 ส่งข้อมูลไป Discord"):
    queue_count = sum(1 for d in st.session_state.doctors if d['status'] == "⏳ คิวต่อไป")
    
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
    elif queue_count > 1:
        st.error(f"❌ ผิดพลาด! มีคนเป็น 'คิวต่อไป' {queue_count} คน (ต้องมีแค่ 1)")
    else:
        # ส่วนเชื่อมต่อ Discord ของคุณ
        st.success("ข้อมูลถูกต้อง! กำลังส่งไปยัง Discord...")
        # requests.post(webhook_url, json={...})
