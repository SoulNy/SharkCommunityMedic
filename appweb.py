import streamlit as st
import json
import os
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Shark Community Medic", page_icon="🚑", layout="wide")

DATA_FILE = 'data.json'
STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

# --- ฟังก์ชันจัดการข้อมูล (JSON) ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"runnerName": "", "doctors": [], "lastUpdated": None}

def save_data(data):
    data["lastUpdated"] = time.time() * 1000  # บันทึกเวลาอัปเดตล่าสุด (มิลลิวินาที)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# รีเฟรชหน้าจออัตโนมัติเงียบๆ ทุก 1 วินาที (1000 มิลลิวินาที) เพื่อให้นาฬิกาเหม่อเดินสดๆ
st_autorefresh(interval=1000, key="medic_realtime_refresh")

# โหลดข้อมูลล่าสุดจากไฟล์ JSON ทุกครั้งที่หน้าจอรันใหม่
app_data = load_data()
st.session_state.app_data = app_data

# ==========================================
# 🎛️ SIDEBAR: แถบเมนูด้านซ้ายสำหรับสลับโหมด
# ==========================================
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
                        app_data["runnerName"] = name_input.strip()
                        save_data(app_data)
                        st.rerun()
        else:
            st.success(f"ผู้รันคิวปัจจุบัน: **{app_data['runnerName']}**")
            if st.button("ลงชื่อออก (Logout)"):
                app_data["runnerName"] = ""
                save_data(app_data)
                st.rerun()

# แปลงรูปแบบเวลาแสดงผลอัปเดตล่าสุด
last_up = app_data.get("lastUpdated")
last_up_text = datetime.fromtimestamp(last_up / 1000).strftime('%d/%m/%Y %H:%M:%S') if last_up else "ยังไม่มีการอัปเดต"

# ==========================================
# 📺 1. หน้าจอสำหรับคนดูอย่างเดียว (READ-ONLY)
# ==========================================
if view_mode == "📺 หน้าจอสำหรับคนดู (Read-Only)":
    st.title("📋 ตารางสถานะแพทย์ Shark Community (สำหรับคนดู)")
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.caption("⚡ ระบบอัปเดตแบบ Real-Time | หน้าจอนี้สำหรับดูข้อมูลอย่างเดียว")
    with col_t2:
        if app_data.get("runnerName"):
            st.markdown(f"🟢 **ผู้คุมคิวเวรวันนี้:** {app_data['runnerName']}")
        else:
            st.markdown("⚪ **ผู้คุมคิวเวรวันนี้:** ไม่มี")
        st.markdown(f"⏳ *อัปเดตล่าสุด: {last_up_text}*")
        
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
            # ⏱️ ระบบคำนวณเวลานับเหม่อสดๆ ฝั่งคนดู
            if doc['status'] == "💤 เหม่อ / รี ตม." and doc.get('lastStatusChange'):
                diff_sec = int(time.time() - (doc['lastStatusChange'] / 1000))
                m, s = divmod(diff_sec, 60)
                status_text += f" ⏱️ เหม่อไปแล้ว {m:02d}:{s:02d} นาที"
                c_status.error(status_text) # ใช้กล่องสีแดงไฮไลท์ตอนเหม่อ
            elif doc['status'] == "⏳ คิวต่อไป":
                c_status.warning(status_text) # ใช้กล่องสีเหลืองแจ้งเตือนคิวถัดไป
            else:
                c_status.info(status_text) # สถานะปกติใช้กล่องน้ำเงินสะอาดตา

# ==========================================
# 🛠️ 2. หน้าจอควบคุม (ADMIN / RUNNER CONTROL)
# ==========================================
else:
    st.title("🚑 [ผู้รันคิว] ระบบจัดการสถานะแพทย์ Shark Community")
    st.caption(f"แก้ไขล่าสุดเมื่อ: {last_up_text}")
    st.markdown("---")
    
    # ฟอร์มเพิ่มรายชื่อแพทย์
    col_add, col_clear = st.columns([3, 1])
    with col_add:
        with st.form("add_doctor_form", clear_on_submit=True):
            new_name = st.text_input("เพิ่มชื่อหมอเข้าคิวเวร:", placeholder="ใส่ชื่อแพทย์ที่นี่...")
            if st.form_submit_button("➕ ลงชื่อเข้าเวร"):
                if new_name.strip():
                    app_data["doctors"].append({
                        "name": new_name.strip(),
                        "status": "✅ พร้อม",
                        "lastStatusChange": time.time() * 1000
                    })
                    save_data(app_data)
                    st.rerun()
                    
    with col_clear:
        st.write("") 
        st.write("") 
        if st.button("🗑️ ล้างคิวทั้งหมด", type="primary"):
            app_data["doctors"] = []
            save_data(app_data)
            st.rerun()
            
    st.markdown("---")
    
    if not app_data["doctors"]:
        st.info("ยังไม่มีรายชื่อแพทย์ในคิวเวร กดเพิ่มชื่อด้านบนได้เลยครับ")
    else:
        h_no, h_name, h_status, h_del = st.columns([1, 3, 5, 1])
        h_no.markdown("**No.**")
        h_name.markdown("**ชื่อแพทย์**")
        h_status.markdown("**สถานะ (คลิกเปลี่ยน)**")
        h_del.markdown("**ลบ**")
        st.markdown("---")
        
        for idx, doc in enumerate(app_data["doctors"]):
            c_no, c_name, c_status, c_del = st.columns([1, 3, 5, 1])
            c_no.write(f"`{idx + 1}`")
            
            # ช่องพิมพ์แก้ไขชื่อหมอแบบ Real-Time
            edited_name = c_name.text_input("ชื่อหมอ", value=doc['name'], key=f"name_{idx}", label_visibility="collapsed")
            if edited_name != doc['name']:
                app_data["doctors"][idx]["name"] = edited_name
                save_data(app_data)
                st.rerun()
                
            # ปุ่มสลับสถานะ
            current_status_idx = STATUS_OPTIONS.index(doc['status']) if doc['status'] in STATUS_OPTIONS else 0
            
            # เติมตัวเลขเวลานับเหม่อสดๆ แปะไว้ข้างหน้าตัวเลือกฝั่งแอดมินด้วย จะได้รู้ว่าใครเหม่อนานแล้ว
            display_options = STATUS_OPTIONS.copy()
            if doc['status'] == "💤 เหม่อ / รี ตม." and doc.get('lastStatusChange'):
                diff_sec = int(time.time() - (doc['lastStatusChange'] / 1000))
                m, s = divmod(diff_sec, 60)
                display_options[3] = f"💤 เหม่อ ({m:02d}:{s:02d})"

            chosen_status = c_status.radio(
                "เปลี่ยนสถานะ", 
                display_options, 
                index=current_status_idx, 
                key=f"status_{idx}", 
                label_visibility="collapsed", 
                horizontal=True
            )
            
            # ลอกข้อความเวลากลับมาเป็นชื่อสถานะเพียวๆ ก่อนเอาไปประมวลผล
            if "💤 เหม่อ" in chosen_status:
                chosen_status = "💤 เหม่อ / รี ตม."
            
            # ⚡ Logic ตรวจจับการเปลี่ยนสถานะ
            if chosen_status != doc['status']:
                # 🔒 กฎเหล็ก: ถ้าคนนี้ถูกตั้งเป็น "คิวต่อไป" คนอื่นทุกคนที่เป็นคิวต่อไปอยู่ จะต้องเด้งกลับเป็น "พร้อม"
                if chosen_status == "⏳ คิวต่อไป":
                    for d_idx, d in enumerate(app_data["doctors"]):
                        if d_idx != idx and d["status"] == "⏳ คิวต่อไป":
                            app_data["doctors"][d_idx]["status"] = "✅ พร้อม"
                            app_data["doctors"][d_idx]["lastStatusChange"] = time.time() * 1000
                            
                # อัปเดตสถานะใหม่และรีเซ็ตเวลาเริ่มต้นนับ (Timestamp) ของคนนี้
                app_data["doctors"][idx]["status"] = chosen_status
                app_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                save_data(app_data)
                st.rerun()
                
            # ปุ่มลบรายคน
            if c_del.button("🗑️", key=f"del_{idx}"):
                app_data["doctors"].pop(idx)
                save_data(app_data)
                st.rerun()
