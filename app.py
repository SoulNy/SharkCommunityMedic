import streamlit as st
import requests
import uuid
import time

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Shark Community Medic", page_icon="🚑", layout="wide")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

WEBHOOK_URL = "https://discord.com/api/webhooks/1510984777648574484/8naHbPVtceUvobVERxizU_8H_2DrRO17ZoqXw_g3pbcD8_MxBAFYUOCw2nnK62cBOuWW"
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

# --- ตารางแสดงผล ---
# ปรับคอลัมน์เพิ่มปุ่มเหม่อ
cols = st.columns([0.5, 3, 2, 1, 0.8])
cols[0].write("**No.**"); cols[1].write("**ชื่อแพทย์**"); cols[2].write("**สถานะ**"); cols[3].write("**เหม่อ/รี**"); cols[4].write("**ลบ**")

for i, doc in enumerate(st.session_state.doctors):
    if 'sleep_start' not in doc: doc['sleep_start'] = None
    if 'alert_sent' not in doc: doc['alert_sent'] = False
    
    c1, c2, c3, c4, c5 = st.columns([0.5, 3, 2, 1, 0.8])
    c1.write(f"{i+1}")
    
    doc['name'] = c2.text_input("ชื่อ", value=doc['name'], key=f"n_{doc['id']}", label_visibility="collapsed")
    
    # ถ้าสถานะเปลี่ยนไปที่ไม่ใช่ "เหม่อ" ให้รีเซ็ตระบบเหม่อ
    if doc['status'] != "💤 เหม่อ / รี ตม.":
        doc['sleep_start'] = None
        doc['alert_sent'] = False
    
    c3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(doc['status']), 
                 key=f"s_{doc['id']}", label_visibility="collapsed", on_change=update_status, args=(doc['id'],))
    
    # ปุ่มเหม่อ/รีตม (คอลัมน์ที่ 4)
    if c4.button("💤" if not doc['sleep_start'] else "⏰", key=f"sleep_{doc['id']}"):
        if not doc['sleep_start']:
            doc['sleep_start'] = time.time()
            doc['status'] = "💤 เหม่อ / รี ตม."
            doc['alert_sent'] = False
        else:
            doc['sleep_start'] = None
            doc['status'] = "✅ พร้อม"
        st.rerun()
        
    # เช็คเวลาครบ 15 นาที (900 วินาที)
    if doc['sleep_start']:
        elapsed = time.time() - doc['sleep_start']
        if elapsed >= 900:
            c3.error("🚨 หมดเวลา!")
            if not doc['alert_sent']:
                requests.post(WEBHOOK_URL, json={"content": f"⚠️ หมอ {doc['name']} หมดเวลาเหม่อ/รีตม. แล้วครับ!"})
                doc['alert_sent'] = True
        else:
            remaining = int(15 - (elapsed / 60))
            c3.caption(f"เหลือ {remaining} นาที")
            
    if c5.button("🗑️", key=f"d_{doc['id']}"):
        st.session_state.doctors.pop(i)
        st.rerun()
