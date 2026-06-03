import streamlit as st
import requests
import uuid
import time
from datetime import datetime

# --- ตั้งค่า Bot ---
BOT_TOKEN = "ใส่_TOKEN_ของคุณที่นี่"
CHANNEL_ID = "ใส่_CHANNEL_ID_ของห้องที่จะให้บอทไปพิมพ์"

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Shark Community Medic", page_icon="🚑", layout="wide")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# --- Initialize Session State ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""
if 'message_id' not in st.session_state: st.session_state.message_id = None

# --- ฟังก์ชัน Callback สำหรับอัปเดตสถานะ ---
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

# --- ส่วนเพิ่มรายชื่อ ---
new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ") and new_name:
    st.session_state.doctors.append({
        "id": str(uuid.uuid4()), 
        "name": new_name, 
        "status": "✅ พร้อม",
        "sleep_start": None,
        "alert_sent": False
    })
    st.rerun()

st.markdown("---")

# --- ตารางแสดงผล ---
cols = st.columns([0.5, 3, 2, 1, 0.8])
cols[0].write("**No.**"); cols[1].write("**ชื่อแพทย์**"); cols[2].write("**สถานะ**"); cols[3].write("**เหม่อ/รี**"); cols[4].write("**ลบ**")

for i, doc in enumerate(st.session_state.doctors):
    if 'sleep_start' not in doc: doc['sleep_start'] = None
    if 'alert_sent' not in doc: doc['alert_sent'] = False
    
    c1, c2, c3, c4, c5 = st.columns([0.5, 3, 2, 1, 0.8])
    c1.write(f"{i+1}")
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    
    if doc['status'] != "💤 เหม่อ / รี ตม.":
        doc['sleep_start'] = None
        doc['alert_sent'] = False
    
    c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), 
                 key=f"s_{doc['id']}", label_visibility="collapsed", on_change=update_status, args=(doc['id'],))
        
    if c4.button("💤" if not doc['sleep_start'] else "⏰", key=f"sleep_{doc['id']}"):
        if not doc['sleep_start']:
            doc['sleep_start'] = time.time()
            doc['status'] = "💤 เหม่อ / รี ตม."
            doc['alert_sent'] = False
        else:
            doc['sleep_start'] = None
            doc['status'] = "✅ พร้อม"
        st.rerun()
        
    if doc['sleep_start']:
        elapsed = time.time() - doc['sleep_start']
        if elapsed >= 900:
            c3.error("🚨 หมดเวลา!")
            if not doc['alert_sent']:
                # แจ้งเตือนใน Discord เมื่อครบเวลา
                requests.post(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages", 
                              headers={"Authorization": f"Bot {BOT_TOKEN}"}, 
                              json={"content": f"⚠️ หมอ {doc['name']} หมดเวลาเหม่อ/รีตม. แล้ว!"})
                doc['alert_sent'] = True
        else:
            c3.caption(f"เหลือ {int(15 - (elapsed / 60))} นาที")

    if c5.button("🗑️", key=f"d_{doc['id']}"):
        st.session_state.doctors.pop(i)
        st.rerun()

# --- ส่วนส่งข้อมูลไป Discord แบบแก้ไขข้อความเดิม ---
st.markdown("---")
if st.button("🚀 อัปเดตตารางใน Discord"):
    message = "🚑 **สถานะทีมแพทย์ Shark Community**\n"
    message += f"🕒 *อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}*\n```\n"
    message += f"{'No.':<4} {'ชื่อแพทย์':<17} | {'สถานะ':<10}\n"
    message += "-" * 40 + "\n"
    for i, doc in enumerate(st.session_state.doctors):
        message += f"{i+1:<4} {doc['name']:<15} | {doc['status']}\n"
    message += "```"
    
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    
    if st.session_state.message_id is None:
        url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
        res = requests.post(url, headers=headers, json={"content": message})
        if res.status_code == 200:
            st.session_state.message_id = res.json()['id']
            st.success("✅ ส่งตารางใหม่เรียบร้อย!")
    else:
        url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{st.session_state.message_id}"
        res = requests.patch(url, headers=headers, json={"content": message})
        if res.status_code == 200:
            st.success("✅ อัปเดตตารางเดิมเรียบร้อย!")
        else:
            # กรณีข้อความถูกลบไป ให้เริ่มส่งใหม่
            st.session_state.message_id = None
            st.error("ไม่พบข้อความเดิม ระบบจะรีเซ็ตให้ส่งใหม่ในครั้งถัดไป")
