# Stock AI Agent SaaS

โปรเจกต์ SaaS สำหรับช่วยส่งคำสั่งซื้อขายหุ้นโดยใช้ AI Agent ที่ติดตามข่าวสารและวิเคราะห์ข้อมูลหุ้น เพื่อช่วยผู้ใช้ตั้ง Limit การซื้อขายและดูสรุปข้อมูลหุ้น เช่น ค่า PE

---

## เทคโนโลยีหลัก (Tech Stack)

- **Frontend:** Next.js (React)  
- **Backend:** FastAPI (Python)  
- **Database:** PostgreSQL  
- **Cache:** Redis  
- **Containerization:** Docker & Docker Compose  
- **Cloud (ในอนาคต):** Azure Cloud  
- **อื่น ๆ ที่กำลังพัฒนา:** Kubernetes, Redis Cache, AI integration

---

## คุณสมบัติหลัก

- ตั้ง Alert หุ้นพร้อม keyword ที่สนใจ  
- AI Agent ดึงข่าวจากแหล่งข่าวหลายแห่ง ผ่าน RSS feed  
- วิเคราะห์ข่าวตาม keyword ที่ตั้งไว้  
- สรุปข้อมูลหุ้น เช่น ค่า PE และ Sentiment จากข่าว  
- ระบบแจ้งเตือน (วางแผนเพิ่ม LINE Notify / Email)  
- รองรับการ deploy บน Azure Cloud

---

## วิธีติดตั้งและใช้งาน (Local Development)

1. Clone repo นี้
   ```bash
   git clone https://github.com/jin-tech/stock-ai-agent-saas.git
   cd stock-ai-agent-saas