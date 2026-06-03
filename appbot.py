import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# --- ตั้งค่า Bot ---
# แนะนำ: ไปที่ Discord Developer Portal เพื่อ Reset Token แล้วนำ Token ใหม่มาใส่ที่นี่
BOT_TOKEN = "MTUxMTU5MDkwMDMwMjg3Njc5Mg.GMI7Pt.Bkyp7rRtroJ2YMtobpnwMsHOizGOCuU_JaIxw4"
CHANNEL_ID = "1511587536298967083"

st.set_page_config(page_title="Shark Community Medic", layout="wide")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# --- Initialize Session State ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""
if 'message_id' not in st.session_state: st.session_state.message_id = None

# --- ฟังก์ชันส่งข้อมูล ---
def sync_to_discord():
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
        return

    # สร้างข้อความตาราง
    message = f"🚑 **สถานะทีมแพทย์ Shark Community**\n👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}\n🕒 {datetime.now().strftime('%H:%M:%S')}\n```\n"
    for i, doc in enumerate(st.session_state.doctors):
        message += f"{i+1}. {doc['name']:<15} | {doc['status']}\n"
    message += "```"
    
    # 1. จัดรูปแบบ JSON ให้รองรับ UTF-8 (ไทย/อีโมจิ)
    # ใช้ ensure_ascii=False เพื่อไม่ให้เป็นรหัสแปลกๆ
    payload = json.dumps({"content": message}, ensure_ascii=False).encode('utf-8')
    
    # 2. ตั้งค่า Headers
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        # พยายามส่ง (POST)
        url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
        res = requests.post(url, headers=headers, data=payload)
        
        if res.status_code == 200:
            st.success("✅ ส่งตารางไปยัง Discord สำเร็จ!")
            st.session_state.message_id = res.json().get('id')
        elif res.status_code == 401:
            st.error("❌ 401 Unauthorized: โปรดตรวจสอบ BOT_TOKEN ในโค้ดว่าถูกต้องหรือไม่")
        else:
            st.error(f"❌ เกิดข้อผิดพลาด (Status: {res.status_code}): {res.text}")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

# --- UI ส่วน Sidebar ---
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

# --- UI ส่วนเพิ่มรายชื่อ ---
new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ"):
    if new_name:
        st.session_state.doctors.append({"id": str(uuid.uuid4()), "name": new_name, "status": "✅ พร้อม"})
        st.rerun()
    else:
        st.warning("กรุณากรอกชื่อก่อนเพิ่ม!")

st.markdown("---")

# --- ตารางแสดงผล ---
for i, doc in enumerate(st.session_state.doctors):
    c1, c2, c3, c4 = st.columns([0.5, 3, 2, 1])
    c1.write(f"{i+1}")
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    doc['status'] = c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), key=f"s_{doc['id']}", label_visibility="collapsed")
    if c4.button("🗑️", key=f"d_{doc['id']}"): 
        st.session_state.doctors.pop(i)
        st.rerun()

if st.button("🚀 อัปเดตตารางใน Discord"):
    sync_to_discord()
