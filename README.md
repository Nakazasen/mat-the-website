# Mạt Thế - Sinh Hoá Nguy Cơ ☣️

> *"Trong bóng tối của ngày tận thế, chỉ có ý chí mới cứu rỗi nhân loại..."*

Website đọc truyện chữ chuyên nghiệp — **Zero-cost · 1000+ CCU · Biohazard UI**

## 🏗️ Kiến Trúc

```
Người dùng → Vercel (Next.js) → FastAPI (Render) → Supabase (metadata)
                                                   ↓
                                          Cloudflare R2 (nội dung .txt)
```

## 📁 Cấu Trúc Thư Mục

```
mat-the-website/
├── frontend/     # Next.js 15 + Tailwind CSS
├── backend/      # FastAPI Python
├── scripts/      # Data pipeline
└── .brain/       # Project context
```

## 🚀 Quick Start

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Upload data
```bash
cd scripts
python upload_data.py --input /path/to/truyen.txt
```

## 🌐 Deploy

- **Frontend:** [Vercel](https://vercel.com) — push `frontend/` lên GitHub → connect Vercel
- **Backend:** [Render](https://render.com) — connect `backend/`, set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Status: 🔨 Building
