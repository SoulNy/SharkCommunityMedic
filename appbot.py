import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# --- ตั้งค่า Bot ---
BOT_TOKEN = "MTUxMTU5MDkwMDMwMjg3Njc5Mg.GMI7Pt.Bkyp7rRtroJ2YMtobpnwMsHOizGOCuU_JaIxw4"
CHANNEL_ID = "1511587536298967083"

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑", layout="wide")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# --- Initialize Session State ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""
if 'message_id' not in st.session_state: st.session_state.message_id = None

# --- ฟังก์ชันจัดการ Discord ---
def get_discord_headers():
    return {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json; charset=utf-8"}

def sync_to_discord():
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
        return

    message = "🚑 **สถานะทีมแพทย์ Shark Community**\n"
    message += f"👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}\n"
    message += f"🕒 *อัปเดตล่าสุด: {datetime.now().strftime('%H:%M:%S')}*\n```\n"
    message += f"{'No.':<4} {'ชื่อแพทย์':<17} | {'สถานะ':<10}\n"
    message += "-" * 40 + "\n"
    for i, doc in enumerate(st.session_state.doctors):
        message += f"{i+1:<4} {doc['name']:<15} | {doc['status']}\n"
    message += "```"
    
    payload = json.dumps({"content": message}, ensure_ascii=False).encode('utf-8')
    
    try:
        if st.session_state.message_id is None:
            res_list = requests.get(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=1", headers={"Authorization": f"Bot {BOT_TOKEN}"})
            if res_list.status_code == 200 and len(res_list.json()) > 0:
                st.session_state.message_id = res_list.json()[0]['id']

        if st.session_state.message_id:
            res = requests.patch(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{st.session_state.message_id}", headers=get_discord_headers(), data=payload)
            if res.status_code == 200:
                st.success("✅ อัปเดตตารางเรียบร้อย!")
                return
        
        res_post = requests.post(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages", headers=get_discord_headers(), data=payload)
        if res_post.status_code == 200:
            st.session_state.message_id = res_post.json()['id']
            st.success("✅ ส่งตารางใหม่เรียบร้อย!")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

# --- UI ส่วน Sidebar (คนรันคิว) ---
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

# --- UI ส่วนจัดการข้อมูล ---
new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ") and new_name:
    st.session_state.doctors.append({"id": str(uuid.uuid4()), "name": new_name, "status": "✅ พร้อม", "sleep_start": None, "alert_sent": False})
    st.rerun()

st.markdown("---")

# ตารางแสดงผล
for i, doc in enumerate(st.session_state.doctors):
    c1, c2, c3, c4, c5 = st.columns([0.5, 3, 2, 1, 0.8])
    c1.write(f"{i+1}")
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), key=f"s_{doc['id']}", label_visibility="collapsed")
    
    if c4.button("💤" if not doc['sleep_start'] else "⏰", key=f"sleep_{doc['id']}"):
        doc['sleep_start'] = time.time() if not doc['sleep_start'] else None
        doc['status'] = "💤 เหม่อ / รี ตม." if doc['sleep_start'] else "✅ พร้อม"
        st.rerun()
    
    if c5.button("🗑️", key=f"d_{doc['id']}"): st.session_state.doctors.pop(i); st.rerun()

if st.button("🚀 อัปเดตตารางใน Discord"):
    sync_to_discord()
