import requests
import time
import uuid

# ลิงก์ API ของคุณ (ตรวจสอบ Port ให้ตรงกับที่รัน main.py)
API_URL = "http://localhost:8000/api/curriculum/local-save"

# รายการไฟล์ PDF
pdf_files = [
    # "https://drive.google.com/file/d/1Z1yqquXlgKTRaK7AEBGMV2fbxUqti3kO/edit",
    "https://drive.google.com/file/d/1EnjPZeeDrSA8ihlqJfHVhAg84uwkXQ2k/edit",
    # "https://drive.google.com/file/d/1I9qBUchBydejWwGgbkpC-IdZFvfg61G-/edit",
    # "https://drive.google.com/file/d/1BuRHEYFGX0uQRJaiAG_Wo8TLnuZfxIZa/edit",
    # "https://drive.google.com/file/d/1Z_0zWJQQCrjyEvivrt1lr4ys6FmfkMmO/edit",
    # "https://drive.google.com/file/d/1gZf4ob2MscXVIodVEDe_Y5RhWfy02On9/view"
]

def send_files():
    print(f"--- เริ่มต้นส่งข้อมูลจำนวน {len(pdf_files)} ไฟล์ ---")
    
    for index, url in enumerate(pdf_files):
        # สร้าง refId แบบสุ่ม (หรือจะใช้ index ก็ได้)
        ref_id = str(uuid.uuid4())
        
        payload = {
            "refId": ref_id,
            "url": url
            # ไม่ต้องส่ง fileName เพราะ API จะไปแกะเอง
        }

        print(f"\n[{index+1}/{len(pdf_files)}] กำลังส่ง: {url}")
        
        try:
            # ยิง Request
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                print(f"✅ สำเร็จ: Server รับงานแล้ว (Response: {response.json().get('message')})")
            else:
                print(f"❌ ผิดพลาด: Status {response.status_code}")
                print(f"Detail: {response.text}")

        except Exception as e:
            print(f"🔥 Error การเชื่อมต่อ: {e}")
            print("ตรวจสอบว่ารัน main.py อยู่หรือไม่")

        # หน่วงเวลา 10 วินาที ก่อนส่งไฟล์ถัดไป (ช้าๆ ไม่รีบ)
        print("⏳ รอ 10 วินาที...")
        time.sleep(10)

    print("\n--- เสร็จสิ้นการส่งข้อมูลทั้งหมด ---")

if __name__ == "__main__":
    send_files()