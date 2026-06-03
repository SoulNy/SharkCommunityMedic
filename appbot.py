import requests
import json

# ใส่ Token และ Channel ID ของคุณตรงนี้
TOKEN = "MTUxMTU5MDkwMDMwMjg3Njc5Mg.GMI7Pt.Bkyp7rRtroJ2YMtobpnwMsHOizGOCuU_JaIxw4"
CHANNEL_ID = "1511587536298967083"

def test_bot_connection():
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"content": "✅ บอททดสอบการเชื่อมต่อ: ระบบทำงานได้ปกติ!"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("สำเร็จ! บอทส่งข้อความเข้าห้องแชทได้แล้ว")
        else:
            print(f"ล้มเหลว! สถานะ: {response.status_code}")
            print("รายละเอียด:", response.text)
    except Exception as e:
        print("เกิดข้อผิดพลาดในการเชื่อมต่อ:", e)

if __name__ == "__main__":
    test_bot_connection()
