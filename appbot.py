import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# --- ตั้งค่า Bot ---
# นำ Token และ Channel ID ของคุณมาใส่ตรงนี้
BOT_TOKEN = "ใส่_TOKEN_ของคุณที่นี่"
CHANNEL_ID = "ใส่_CHANNEL_ID_ที่นี่"

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Shark Community Medic", page_icon="🚑", layout="wide")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# --- Initialize Session State ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""
if 'message_id' not in st.session_state: st.session_state.message_id = None

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

# --- Sidebar ---
with st.sidebar:
    if st.button("ออกจากระบบ"):
        st.session_state.runner_name = ""
        st.rerun()

# --- ตารางแสดงผล ---
cols = st.columns([0.5, 3, 2, 1, 0.8])
cols[0].write("**No.**"); cols[1].write("**ชื่อแพทย์**"); cols[2].write("**สถานะ**"); cols[3].write("**เหม่อ/รี**"); cols[4].write("**ลบ**")

for i, doc in enumerate(st.session_state.doctors):
    if 'sleep_start' not in doc: doc['sleep_start'] = None
    if 'alert_sent' not in doc: doc['alert_sent'] = False
    
    c1, c2, c3, c4, c5 = st.columns([0.5, 3, 2, 1, 0.8])
    c1.write(f"{i+1}")
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    
    c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), 
                 key=f"s_{doc['id']}", label_visibility="collapsed", on_change=update_status, args=(doc['id'],))
    
    # ปุ่มเหม่อ
    if c4.button("💤" if not doc['sleep_start'] else "⏰", key=f"sleep_{doc['id']}"):
        if not doc['sleep_start']:
            doc['sleep_start'] = time.time(); doc['status'] = "💤 เหม่อ / รี ตม."; doc['alert_sent'] = False
        else:
            doc['sleep_start'] = None; doc['status'] = "✅ พร้อม"
        st.rerun()
        
    # เช็ค 15 นาที
    if doc['sleep_start']:
        elapsed = time.time() - doc['sleep_start']
        if elapsed >= 900:
            c3.error("🚨 หมดเวลา!")
            if not doc['alert_sent']:
                requests.post(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages", 
                              headers={"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"},
                              data=json.dumps({"content": f"⚠️ หมอ {doc['name']} หมดเวลาเหม่อ/รีตม. แล้ว!"}, ensure_ascii=False).encode('utf-8'))
                doc['alert_sent'] = True
        else:
            c3.caption(f"เหลือ {int(15 - (elapsed / 60))} นาที")

    if c5.button("🗑️", key=f"d_{doc['id']}"):
        st.session_state.doctors.pop(i); st.rerun()

# --- ส่วนส่งข้อมูลไป Discord แบบแก้ไขข้อความ (UTF-8) ---
st.markdown("---")
if st.button("🚀 อัปเดตตารางใน Discord"):
    message = "🚑 **สถานะทีมแพทย์ Shark Community**\n"
    message += f"🕒 *อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}*\n```\n"
    message += f"{'No.':<4} {'ชื่อแพทย์':<17} | {'สถานะ':<10}\n"
    message += "-" * 40 + "\n"
    for i, doc in enumerate(st.session_state.doctors):
        message += f"{i+1:<4} {doc['name']:<15} | {doc['status']}\n"
    message += "```"
    
    payload = json.dumps({"content": message}, ensure_ascii=False).encode('utf-8')
    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}
    
    try:
        if st.session_state.message_id is None:
            res = requests.post(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages", headers=headers, data=payload)
            if res.status_code == 200:
                st.session_state.message_id = res.json()['id']
                st.success("✅ ส่งตารางใหม่เรียบร้อย!")
        else:
            res = requests.patch(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{st.session_state.message_id}", headers=headers, data=payload)
            if res.status_code == 200:
                st.success("✅ อัปเดตตารางเดิมเรียบร้อย!")
            else:
                st.session_state.message_id = None
                st.error("ไม่พบข้อความเดิม ระบบจะรีเซ็ตให้ส่งใหม่")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
