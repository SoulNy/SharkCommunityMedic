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

# --- ฟังก์ชันอ่าน/เขียนไฟล์ (JSON) แบบบังคับเคลียร์แคช ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            # ล้างแคชการอ่านไฟล์เพื่อให้ได้ข้อมูลสดใหม่จากเซิร์ฟเวอร์จริงๆ
            if hasattr(os, 'sync'): os.sync()
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"runnerName": "", "doctors": [], "lastUpdated": None}

def save_data(data):
    data["lastUpdated"] = time.time() * 1000
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 🔌 สั่งแอบดึงข้อมูลรีเฟรชเงียบๆ ทุกๆ 1 วินาที (เพื่อให้คนอื่นเห็นการเปลี่ยนแปลงทันที)
st_autorefresh(interval=1000, key="medic_force_realtime_v2")

# โหลดข้อมูลจริงล่าสุดเข้าสู่ระบบ ณ วินาทีนั้น
app_data = load_data()

# ==========================================
# 🎛️ SIDEBAR: เมนูสลับหน้าจอ
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

# แสดงเวลาอัปเดตล่าสุด
last_up = app_data.get("lastUpdated")
last_up_text = datetime.fromtimestamp(last_up / 1000).strftime('%d/%m/%Y %H:%M:%S') if last_up else "ยังไม่มีการอัปเดต"

# ==========================================
# 📺 1. หน้าจอสำหรับคนดูอย่างเดียว (READ-ONLY)
# ==========================================
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
            if doc['status'] == "💤 เหม่อ / รี ตม." and doc.get('lastStatusChange'):
                diff_sec = int(time.time() - (doc['lastStatusChange'] / 1000))
                m, s = divmod(diff_sec, 60)
                status_text += f" ⏱️ เหม่อไปแล้ว {m:02d}:{s:02d} นาที"
                c_status.error(status_text)
            elif doc['status'] == "⏳ คิวต่อไป":
                c_status.warning(status_text)
            else:
                c_status.info(status_text)

# ==========================================
# 🛠️ 2. หน้าจอควบคุม (ADMIN / RUNNER CONTROL)
# ==========================================
else:
    st.title("🚑 [ผู้รันคิว] ระบบจัดการสถานะแพทย์ Shark Community")
    st.caption(f"แก้ไขล่าสุดเมื่อ: {last_up_text}")
    st.markdown("---")
    
    # ฟอร์มเพิ่มชื่อหมอ
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
        # หัวข้อตารางโฉมใหม่
        h_no, h_name, h_status, h_action, h_del = st.columns([0.5, 2.5, 2, 4, 1])
        h_no.markdown("**No.**")
        h_name.markdown("**ชื่อแพทย์**")
        h_status.markdown("**สถานะปัจจุบัน**")
        h_action.markdown("**คำสั่งเปลี่ยนสถานะ**")
        h_del.markdown("**ลบ**")
        st.markdown("---")
        
        for idx, doc in enumerate(app_data["doctors"]):
            c_no, c_name, c_status, c_action, c_del = st.columns([0.5, 2.5, 2, 4, 1])
            
            # 1. แสดงลำดับ
            c_no.write(f"`{idx + 1}`")
            
            # 2. แก้ไขชื่อหมอ
            edited_name = c_name.text_input("ชื่อหมอ", value=doc['name'], key=f"name_{idx}", label_visibility="collapsed")
            if edited_name != doc['name']:
                current_data = load_data()
                if idx < len(current_data["doctors"]):
                    current_data["doctors"][idx]["name"] = edited_name
                    save_data(current_data)
                    st.rerun()
            
            # 3. แสดงสถานะปัจจุบัน (พร้อมนับเวลาเหม่อ)
            status_text = doc['status']
            if doc['status'] == "💤 เหม่อ / รี ตม." and doc.get('lastStatusChange'):
                diff_sec = int(time.time() - (doc['lastStatusChange'] / 1000))
                m, s = divmod(diff_sec, 60)
                status_text += f" ({m:02d}:{s:02d})"
            c_status.code(status_text)
            
            # 4. ปุ่มคำสั่งต่างๆ (แยกชิ้นกดง่าย ไม่บั๊กแน่นอน)
            btn_col1, btn_col2, btn_col3, btn_col4 = c_action.columns(4)
            
            # ปุ่มพร้อม
            if doc['status'] != "✅ พร้อม":
                if btn_col1.button("✅ พร้อม", key=f"btn_ready_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "✅ พร้อม"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()
            
            # 🔥 ปุ่มคิวต่อไป (Logic แซงคิวหนึ่งเดียว!)
            if doc['status'] != "⏳ คิวต่อไป":
                if btn_col2.button("⏳ คิวถัดไป", key=f"btn_next_{idx}", use_container_width=True, type="secondary"):
                    current_data = load_data()
                    # 🔒 สั่งให้คนอื่นทุกคนที่เป็น คิวต่อไป อยู่ เด้งกลับเป็น พร้อม ทันที!
                    for d_idx, d in enumerate(current_data["doctors"]):
                        if d["status"] == "⏳ คิวต่อไป":
                            current_data["doctors"][d_idx]["status"] = "✅ พร้อม"
                            current_data["doctors"][d_idx]["lastStatusChange"] = time.time() * 1000
                    
                    # ตั้งให้คนล่าสุดคนนี้เป็น คิวต่อไป
                    current_data["doctors"][idx]["status"] = "⏳ คิวต่อไป"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()
            
            # ปุ่มเคสแก้
            if doc['status'] != "🛠️ เคสแก้":
                if btn_col3.button("🛠️ แก้", key=f"btn_fix_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "🛠️ เคสแก้"
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()
                    
            # ปุ่มเหม่อ
            if doc['status'] != "💤 เหม่อ / รี ตม.":
                if btn_col4.button("💤 เหม่อ", key=f"btn_afk_{idx}", use_container_width=True):
                    current_data = load_data()
                    current_data["doctors"][idx]["status"] = "💤 เหม่อ / รี ตม."
                    current_data["doctors"][idx]["lastStatusChange"] = time.time() * 1000
                    save_data(current_data)
                    st.rerun()

            # 5. ปุ่มลบรายคน
            if c_del.button("🗑️", key=f"del_{idx}"):
                current_data = load_data()
                if idx < len(current_data["doctors"]):
                    current_data["doctors"].pop(idx)
                    save_data(current_data)
                    st.rerun()
