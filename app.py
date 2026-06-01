import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# --- ตั้งค่า Webhook ตรงนี้ ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux"

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""

# --- Callback Function ---
def update_status(index):
    new_val = st.session_state[f"s_{index}"]
    if new_val == "⏳ คิวต่อไป":
        for i in range(len(st.session_state.doctors)):
            if i != index and st.session_state.doctors[i]['status'] == "⏳ คิวต่อไป":
                st.session_state.doctors[i]['status'] = "✅ พร้อม"
    st.session_state.doctors[index]['status'] = new_val

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
    
    col3.selectbox(
        "สถานะ", 
        STATUS_OPTIONS, 
        index=STATUS_OPTIONS.index(doc['status']), 
        key=f"s_{i}", 
        label_visibility="collapsed",
        on_change=update_status,
        args=(i,)
    )
    
    if col4.button("ลบ", key=f"d_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# --- ส่ง Discord (รูปแบบตาม image_0a44a7.png) ---
st.markdown("---")
if st.button("🚀 ส่งข้อมูลไป Discord"):
    queue_count = sum(1 for d in st.session_state.doctors if d['status'] == "⏳ คิวต่อไป")
    
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
    elif queue_count > 1:
        st.error(f"❌ ผิดพลาด! มีคนเป็น 'คิวต่อไป' {queue_count} คน (ต้องมีแค่ 1)")
    else:
        message = "🚑 **สถานะทีมแพทย์ Shark Community**\n"
        message += "```\n"
        message += f"{'No.':<4} {'ชื่อแพทย์':<15} | {'สถานะ':<10}\n"
        message += "-" * 40 + "\n"
        
        for i, doc in enumerate(st.session_state.doctors):
            # แสดงชื่อเต็มตามที่ต้องการ
            message += f"{i+1:<4} {doc['name']:<15} | {doc['status']}\n"
        
        message += "```"
        
        data = {"content": message}
        try:
            response = requests.post(WEBHOOK_URL, json=data)
            if response.status_code == 204:
                st.success("✅ ส่งข้อมูลไป Discord เรียบร้อยแล้ว!")
            else:
                st.error(f"เกิดข้อผิดพลาดในการส่ง: {response.status_code}")
        except Exception as e:
            st.error(f"ไม่สามารถเชื่อมต่อ Discord ได้: {e}")
