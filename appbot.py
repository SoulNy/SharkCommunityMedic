import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# --- ตั้งค่า ---
BOT_TOKEN = "MTUxMTU5MDkwMDMwMjg3Njc5Mg.GMI7Pt.Bkyp7rRtroJ2YMtobpnwMsHOizGOCuU_JaIxw4"
CHANNEL_ID = "1511587536298967083"

st.set_page_config(page_title="Shark Community Medic", layout="wide")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# --- Session State ---
if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""
if 'message_id' not in st.session_state: st.session_state.message_id = None

# --- ฟังก์ชันส่ง Discord แบบชัวร์ 100% ---
def sync_to_discord():
    if not st.session_state.runner_name:
        st.error("กรุณาระบุชื่อผู้รันคิวก่อน!")
        return

    # สร้างข้อความ
    message = f"🚑 **สถานะทีมแพทย์ Shark Community**\n👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}\n🕒 {datetime.now().strftime('%H:%M:%S')}\n```\n"
    for i, doc in enumerate(st.session_state.doctors):
        message += f"{i+1}. {doc['name']:<15} | {doc['status']}\n"
    message += "```"
    
    # แก้ปัญหา UnicodeEncodeError ด้วยการทำ JSON payload ที่ระบุ utf-8 ชัดเจน
    payload = json.dumps({"content": message}, ensure_ascii=False).encode('utf-8')
    headers = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json; charset=utf-8"}
    
    try:
        # 1. ถ้าไม่มี message_id ให้หาข้อความล่าสุดของบอทในช่องนั้น
        if st.session_state.message_id is None:
            res_list = requests.get(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=1", headers={"Authorization": f"Bot {BOT_TOKEN}"})
            if res_list.status_code == 200 and len(res_list.json()) > 0:
                st.session_state.message_id = res_list.json()[0]['id']

        # 2. พยายามแก้ไขข้อความเดิม (PATCH)
        if st.session_state.message_id:
            res = requests.patch(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages/{st.session_state.message_id}", headers=headers, data=payload)
            if res.status_code == 200:
                st.success("✅ อัปเดตตารางเรียบร้อย!")
                return
            else:
                st.session_state.message_id = None # ถ้าแก้ไขไม่ได้ (เช่น โดนลบ) ให้เคลียร์ค่า

        # 3. ถ้าไม่มี message_id หรือแก้ไขไม่ได้ ให้ส่งใหม่ (POST)
        res_post = requests.post(f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages", headers=headers, data=payload)
        if res_post.status_code == 200:
            st.session_state.message_id = res_post.json()['id']
            st.success("✅ ส่งตารางใหม่เรียบร้อย!")
        else:
            st.error(f"ส่งไม่สำเร็จ: {res_post.status_code}")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

# --- UI Sidebar ---
with st.sidebar:
    if not st.session_state.runner_name:
        runner_input = st.text_input("ชื่อผู้รันคิว:")
        if st.button("ยืนยันตัวตน"):
            st.session_state.runner_name = runner_input
            st.rerun()
    else:
        st.write(f"👨‍⚕️ รันคิวโดย: **{st.session_state.runner_name}**")
        if st.button("ออกจากระบบ"): st.session_state.runner_name = ""; st.rerun()

# --- UI หลัก ---
new_name = st.text_input("เพิ่มชื่อหมอ:")
if st.button("เพิ่มชื่อ"):
    st.session_state.doctors.append({"id": str(uuid.uuid4()), "name": new_name, "status": "✅ พร้อม"})
    st.rerun()

for i, doc in enumerate(st.session_state.doctors):
    c1, c2, c3, c4 = st.columns([0.5, 3, 2, 1])
    c1.write(i+1)
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    doc['status'] = c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), key=f"s_{doc['id']}", label_visibility="collapsed")
    if c4.button("🗑️", key=f"d_{doc['id']}"): st.session_state.doctors.pop(i); st.rerun()

if st.button("🚀 อัปเดตตารางใน Discord"): sync_to_discord()
