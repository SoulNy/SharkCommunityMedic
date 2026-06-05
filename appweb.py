import streamlit as st
import json
import os
import time
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑", layout="wide")

DATA_FILE = 'data.json'
STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]
APP_URL = "https://appwebpy-tv5hqkpzrlalag7noznbfu.streamlit.app/"

DISCORD_WEBHOOK_URL = "https://ptb.discord.com/api/webhooks/1510984777648574484/8naHbPVtceUvobVERxizU_8H_2DrRO17ZoqXw_g3pbcD8_MxBAFYUOCw2nnK62cBOuWW"

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, key="medic_realtime_clock_v10")
except Exception as e:
    st.warning("⚠️ แนะนำให้ติดตั้ง streamlit-autorefresh เพื่อระบบเวลาที่เรียลไทม์")

def get_thailand_time():
    return datetime.utcnow() + timedelta(hours=7)

def send_to_discord(message_content, embed_title, embed_desc, color_code):
    if DISCORD_WEBHOOK_URL and "discord.com" in DISCORD_WEBHOOK_URL:
        discord_timestamp = datetime.utcnow().isoformat()
        
        payload = {
            "content": message_content,
            "embeds": [
                {
                    "title": embed_title,
                    "description": embed_desc,
                    "color": color_code,
                    "timestamp": discord_timestamp
                }
            ]
        }
        try:
            requests.post(DISCORD_WEBHOOK_URL, json=payload)
        except Exception as e:
            pass

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            if hasattr(os, 'sync'): os.sync()
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass

    return {"runnerName": "", "runnerStartTime": None, "doctors": [], "lastUpdated": None}

def save_data(data):
    data["lastUpdated"] = time.time() * 1000
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


app_data = load_data()

with st.sidebar:
    st.header("⚙️ เมนูการใช้งาน")
    view_mode = st.radio("เลือกหน้าจอที่ต้องการดู:", ["📺 หน้าจอสำหรับคนดู (Read-Only)", "🛠️ หน้าจอควบคุม (Admin/Runner)"])
    
    st.markdown("---")
    
    if view_mode == "🛠️ หน้าจอควบคุม (Admin/Runner)":
        st.subheader("👨‍⚕️ ผู้ควบคุมคิว")
        
        if not app_data.get("runnerName"):
            with st.form("runner_form", clear_on_submit=True):
                name_input = st.text_input("ใส่ชื่อของคุณเพื่อคุมคิว:")
                if st.form_submit_button("ยืนยันตัวตน"):
                    if name_input.strip():
                        current_time_str = get_thailand_time().strftime('%H:%M:%S น.')
                        runner_name = name_input.strip()
                        
                        # บันทึกชื่อ และ เวลาเริ่มเข้าเวร (ใช้หน่วยวินาที epoch)
                        app_data["runnerName"] = runner_name
                        app_data["runnerStartTime"] = time.time()
                        save_data(app_data)
                        
                        send_to_discord(
                            message_content=f"🔔 **มีอัปเดตผู้คุมเวรแพทย์ล่าสุดจ้า!**",
                            embed_title="🟢 หมอเข้าเวรรันคิวแล้วครับ",
                            embed_desc=f"**ผู้รันคิว:** {runner_name}\n**เวลาเริ่ม:** {current_time_str}\n\n📌 สามารถกดดูคิวอัปเดตสดๆ ในโหมดคนดูได้ที่ลิงก์ด้านล่างนี้เลยครับ:\n👉 [Shark Community Medic · Streamlit]({APP_URL})",
                            color_code=3066993
                        )
                        st.rerun()
        
        else:
            st.success(f"ผู้รันคิวปัจจุบัน: **{app_data['runnerName']}**")
            if st.button("ลงชื่อออก (Logout)"):
                current_time_str = get_thailand_time().strftime('%H:%M:%S น.')
                old_runner = app_data["runnerName"]
                start_time = app_data.get("runnerStartTime")
                
                # คำนวณเวลารวมที่อยู่ในเวร
                duration_text = "ไม่สามารถคำนวณได้"
                if start_time:
                    total_seconds = int(time.time() - start_time)
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    if hours > 0:
                        duration_text = f"{hours} ชั่วโมง {minutes} นาที"
                    else:
                        duration_text = f"{minutes} นาที {seconds} วินาที"
                
                app_data["runnerName"] = ""
                app_data["runnerStartTime"] = None
                save_data(app_data)
                
                send_to_discord(
                    message_content=f"📴 **ผู้คุมเวรแพทย์ลงชื่อออกแล้วจ้า!**",
                    embed_title="🔴 หมอลงชื่อออกเวรแล้วครับ",
                    embed_desc=f"**ผู้รันคิวเดิม:** {old_runner}\n**เวลาออก:** {current_time_str}\n**⏱️ รวมเวลาคุมเวรทั้งหมด:** {duration_text}\n\n📌 ยังสามารถเข้าดูสถานะที่ค้างอยู่ล่าสุดของแพทย์คนอื่นๆ ได้ที่ลิงก์เดิมน้า:\n👉 [Shark Community Medic · Streamlit]({APP_URL})",
                    color_code=15158332
                )
                st.rerun()

last_up = app_data.get("lastUpdated")
last_up_text = datetime.fromtimestamp(last_up / 1000).strftime('%d/%m/%Y %H:%M:%S') if last_up else "ยังไม่มีการอัปเดต"

if view_mode == "📺 หน้าจอสำหรับคนดู (Read-Only)":
    st.title("📋 ตารางสถานะแพทย์ Shark Community (สำหรับคนดู)")
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.caption("⚡ ระบบอัปเดตอัตโนมัติแบบ Real-Time")
    with col_t2:
        if app_data.get("runnerName"):
            st.markdown(f"🟢 **ผู้คุมคิวเวรวันนี้:** {app_data['runnerName']}")
        else:
            st.markdown("⚪ **ผู้คุมคิวเวรวันนี้:** ไม่มี")
        # st.markdown(f"⏳ *อัปเดตล่าสุด: {last_up_text}*")
        
    st.markdown("---")
    
    with st.expander("➕ คลิกที่นี่เพื่อลงชื่อเข้าคิวด้วยตัวเอง", expanded=False):
        st.markdown("##### กรุณากรอกชื่อของคุณเพื่อเพิ่มรายชื่อเข้าสู่ระบบคิวกลาง")
        
        with st.form("user_register_form", clear_on_submit=True):
            user_name_input = st.text_input("ชื่อแพทย์:", placeholder="กรอกชื่อของคุณ / กรอกเป็นคู่")
            submit_reg = st.form_submit_button("ยืนยันลงชื่อเข้าเวร", type="primary")
            
            if submit_reg:
                if user_name_input.strip():
                    current_data = load_data()
                    current_data["doctors"].append({
                        "name": user_name_input.strip(),
                        "status": "✅ พร้อม",
                        "lastStatusChange": time.time() * 1000
                    })
                    save_data(current_data)
                    st.success(f"เพิ่มชื่อคุณ **{user_name_input.strip()}** เข้าสู่คิวเรียบร้อยแล้ว!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("กรุณากรอกชื่อก่อนกดปุ่มยืนยันครับ")
            
    st.markdown("---")
    
    if not app_data["doctors"]:
        st.info("ยังไม่มีรายชื่อแพทย์ในคิวเวรในขณะนี้")
    else:
        h_no, h_name, h_status = st.columns([1, 4, 5])
        h_no.markdown("**No.**")
        h_name.markdown("**ชื่อแพทย์**")
        h_status.markdown("**สถานะปัจจุบัน**")
        st.markdown("---")
        
        for idx, doc in enumerate(app_data["doctors"]):
            c_no, c_name, c_status = st.columns([1, 4, 5])
            c_no.write(f"`{idx + 1}`")
            c_name.markdown(f"**{doc['name']}**")
            
            status_text = doc['status']
            if doc['status'] == "💤 เหม่อ / รี ตม." and doc.get('lastStatusChange'):
                diff_sec = int(time.time() - (doc['lastStatusChange'] / 1000))
                m, s = divmod(diff_sec, 60)
                status_text += f" ⏱️ เหม่อไปแล้ว {m:02d}:{s:02d} นาที"
                c_status.error(status_text)
            elif doc['status'] == "⏳ คิวต่อไป":
                c_status.warning(status_text)
            elif doc['status'] == "🎮 ไปกิจกรรม":
                c_status.info(status_text)
            else:
                c_status.info(status_text)

else:
    st.title("🚑 [ผู้รันคิว] ระบบจัดการสถานะแพทย์ Shark Community")
    st.caption(f"แก้ไขล่าสุดเมื่อ: {last_up_text}")
    st.markdown("---")
    
    col_add, col_clear = st.columns([3, 1])
    with col_add:
        with st.form("add_doctor_form", clear_on_submit=True):
            new_name = st.text_input("เพิ่มชื่อหมอเข้าคิวเวร:", placeholder="ใส่ชื่อแพทย์ที่นี่...")
            if st.form_submit_button("➕ ลงชื่อเข้าเวร"):
                if new_name.strip():
                    current_data = load_data()
                    current_data["doctors"].append({
                        "name": new_name.strip(),
                        "status": "✅ พร้อม",
                        "lastStatusChange": time.time() * 1000
                    })
                    save_data(current_data)
                    st.rerun()
                    
    with col_clear:
        st.write("") 
        st.write("") 
        if st.button("🗑️ ล้างคิวทั้งหมด", type="primary"):
            current_data = load_data()
            current_data["doctors"] = []
            save_data(current_data)
            st.rerun()
            
    st.markdown("---")
    
    if not app_data["doctors"]:
        st.info("ยังไม่มีรายชื่อแพทย์ในคิวเวร กดเพิ่มชื่อด้านบนได้เลยครับ")
    else:
        h_no, h_name, h_status, h_action, h_del = st.columns([0.5, 2.0, 2.0, 5.0, 0.5])
        h_no.markdown("**No.**")
        h_name.markdown("**ชื่อแพทย์**")
        h_status.markdown("**สถานะปัจจุบัน**")
        h_action.markdown("**คำสั่งเปลี่ยนสถานะ**")
        h_del.markdown("**ลบ**")
        st.markdown("---")
        
        for idx, doc in enumerate(app_data["doctors"]):
            c_no, c_name, c_status, c_action, c_del = st.columns([0.5, 2.0, 2.0, 5.0, 0.5])
            c_no.write(f"`{idx + 1}`")
            
            edited_name = c_name.text_input("ชื่อหมอ", value=doc['name'], key=f"name_{idx}", label_visibility="collapsed")
            if edited_name != doc['name']:
                current_data = load_data()
                if idx < len(current_data["doctors"]):
                    current_data["doctors"][idx]["name"] = edited_name
                    save_data(current_data)
                    st.rerun()
            
            status_text = doc['status']
            if doc['status'] == "💤 เหม่อ / รี ตม." and doc.get('lastStatusChange'):
                diff_sec = int(time.time() - (doc['lastStatusChange'] / 1000))
                m, s = divmod(diff_sec, 60)
                status_text += f" ({m:02d}:{s:02d})"
            c_status.code(status_text)
            
            btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = c_action.columns(5)
            
            if doc['status'] != "✅ พร้อม":
                if btn_col1.button("✅ พร้อม", key=f"btn_ready_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "✅ พร้อม"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()
            
            if doc['status'] != "⏳ คิวต่อไป":
                if btn_col2.button("⏳ ถัดไป", key=f"btn_next_{idx}", use_container_width=True, type="secondary"):
                    current_data = load_data()
                    for d_idx, d in enumerate(current_data["doctors"]):
                        if d["status"] == "⏳ คิวต่อไป":
                            current_data["doctors"][d_idx]["status"] = "✅ พร้อม"
                            current_data["doctors"][d_idx]["lastStatusChange"] = time.time() * 1000
                    
                    current_data["doctors"][idx]["status"] = "⏳ คิวต่อไป"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()
            
            if doc['status'] != "🛠️ เคสแก้":
                if btn_col3.button("🛠️ แก้", key=f"btn_fix_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "🛠️ เคสแก้"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()
                    
            if doc['status'] != "💤 เหม่อ / รี ตม.":
                if btn_col4.button("💤 เหม่อ", key=f"btn_afk_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "💤 เหม่อ / รี ตม."
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()

            if doc['status'] != "🎮 ไปกิจกรรม":
                if btn_col5.button("🎮 กิจกรรม", key=f"btn_event_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "🎮 ไปกิจกรรม"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()

            if c_del.button("🗑️", key=f"del_{idx}"):
                current_data = load_data()
                if idx < len(current_data["doctors"]):
                    current_data["doctors"].pop(idx)
                    save_data(current_data)
                    st.rerun()
