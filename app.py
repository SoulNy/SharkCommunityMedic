import streamlit as st
import requests

st.set_page_config(page_title="Shark Community Medic", page_icon="🚑")
st.title("🚑 ระบบจัดการสถานะแพทย์ Shark Community")

# สถานะทั้งหมด
STATUS_OPTIONS = ["✅ พร้อม", "⏳ คิวต่อไป", "🛠️ เคสแก้", "💤 เหม่อ / รี ตม.", "🎮 ไปกิจกรรม"]

if 'doctors' not in st.session_state: st.session_state.doctors = []
if 'runner_name' not in st.session_state: st.session_state.runner_name = ""

# Sidebar
with st.sidebar:
    st.subheader("⚙️ ตั้งค่ารันคิว")
    if not st.session_state.runner_name:
        runner_input = st.text_input("ใส่ชื่อผู้รันคิวของคุณ:")
        if st.button("ยืนยันตัวตน"):
            st.session_state.runner_name = runner_input
            st.rerun()
    else:
        st.success(f"👨‍⚕️ ผู้รันคิว: {st.session_state.runner_name}")
        if st.button("ออกจากระบบ"):
            st.session_state.runner_name = ""
            st.rerun()

webhook_url = st.text_input("Webhook URL:", value="https://discord.com/api/webhooks/1510897665020530781/thYbEXxxQkhbdLaSPPqVUCIUhyXP7ynp4gJs4By-Q92HS2MpqZQqoIbLDNkBYSyrrlux")
new_name = st.text_input("เพิ่มชื่อหมอ:")

if st.button("เพิ่มชื่อ"):
    if not st.session_state.runner_name:
        st.error("กรุณายืนยันชื่อผู้รันคิวในเมนูด้านซ้ายก่อน!")
    elif new_name:
        st.session_state.doctors.append({"name": new_name, "status": "✅ พร้อม"})
        st.rerun()

# --- ส่วนแสดงตาราง ---
st.write(f"**แพทย์รันคิว :** {st.session_state.runner_name if st.session_state.runner_name else 'ยังไม่มีผู้รัน'}")
st.markdown("---")

# หัวตาราง
head1, head2, head3 = st.columns([1, 4, 3])
head1.write("**No.**")
head2.write("**ชื่อแพทย์**")
head3.write("**สถานะ**")

# รายชื่อแพทย์
for i, doc in enumerate(st.session_state.doctors):
    col1, col2, col3, col4 = st.columns([1, 4, 3, 1])
    
    col1.write(f"{i+1}")
    col2.write(f"{doc['name']}")
    
    old_status = doc['status']
    new_status = col3.selectbox("สถานะ", STATUS_OPTIONS, index=STATUS_OPTIONS.index(old_status), key=f"s_{i}", label_visibility="collapsed")
    
    # Logic: "คิวต่อไป" มีได้คนเดียว
    if new_status != old_status:
        if new_status == "⏳ คิวต่อไป":
            for j, d in enumerate(st.session_state.doctors):
                if i != j and d['status'] == "⏳ คิวต่อไป":
                    st.session_state.doctors[j]['status'] = "✅ พร้อม"
        doc['status'] = new_status
        st.rerun()
    
    if col4.button("ลบ", key=f"d_{i}"):
        st.session_state.doctors.pop(i)
        st.rerun()

st.markdown("---")
if st.button("🚀 ส่งข้อมูลไป Discord"):
    if not st.session_state.runner_name:
        st.error("ต้องมีชื่อผู้รันคิวก่อนถึงจะส่งได้ครับ!")
    else:
        content = f"🚑 **สถานะทีมแพทย์ (อัปเดตโดย: {st.session_state.runner_name})**\n```\n"
        content += f"{'No.':<4} {'ชื่อแพทย์':<15} | {'สถานะ'}\n"
        content += "-"*40 + "\n"
        for i, doc in enumerate(st.session_state.doctors):
            content += f"{i+1:<4} {doc['name']:<15} | {doc['status']}\n"
        content += "```"
        requests.post(webhook_url, json={"content": content})
        st.success("ส่งข้อมูลไป Discord เรียบร้อย!")
