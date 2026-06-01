import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""

# ส่วน Sidebar และเพิ่มชื่อ (คงเดิม)
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

# --- ตารางแสดงผลที่ปรับปรุง Logic แล้ว ---
st.markdown("---")
head1, head2, head3 = st.columns([1, 4, 3])
head1.write("**No.**"); head2.write("**ชื่อแพทย์**"); head3.write("**สถานะ**")

for i, doc in enumerate(st.session_state.doctors):
    col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
    col1.write(f"{i+1}")
    col2.write(f"{doc['name']}")
    
    # ดึงค่าสถานะปัจจุบัน
    current_status = doc['status']
    
    # เลือกสถานะใหม่
    new_status = col3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current_status), key=f"s_{i}", label_visibility="collapsed")
    
    # ปรับ Logic: ถ้าเลือก "คิวต่อไป" ให้คนอื่นที่เหลือเป็น "พร้อม" ทันที
    if new_status != current_status:
        if new_status == "⏳ คิวต่อไป":
            for j in range(len(st.session_state.doctors)):
                if j != i:
                    if st.session_state.doctors[j]['status'] == "⏳ คิวต่อไป":
                        st.session_state.doctors[j]['status'] = "✅ พร้อม"
        
        doc['status'] = new_status
        st.rerun() # รีโหลดหน้าจอเพื่ออัปเดตข้อมูลให้ตรงกันทั้งตาราง
        
    if col4.button("ลบ", key=f"d_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# --- ส่ง Discord แบบเช็คความถูกต้องก่อนส่ง ---
if st.button("🚀 ส่งข้อมูลไป Discord"):
    # ตรวจสอบซ้ำก่อนส่ง: คิวต่อไปต้องมีไม่เกิน 1 คน
    queue_count = sum(1 for d in st.session_state.doctors if d['status'] == "⏳ คิวต่อไป")
    
    if queue_count > 1:
        st.error(f"❌ ผิดพลาด! มีคนเป็น 'คิวต่อไป' {queue_count} คน (ต้องมีแค่ 1)")
    elif not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
    else:
        # (ส่วนโค้ดส่ง Discord เหมือนเดิม)
        st.success("ข้อมูลถูกต้อง! กำลังส่ง...")
