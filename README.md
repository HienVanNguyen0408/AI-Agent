# 🤖 AI Agent với Google LLM + LangGraph

Dự án này xây dựng một AI Agent sử dụng LLM của Google (Gemini Pro hoặc PaLM) kết hợp với LangGraph để xử lý hội thoại có trạng thái, ghi nhớ lịch sử, và dễ dàng mở rộng.

---

## 🚀 Tính năng

- Kết nối Google Generative AI (Gemini Pro)
- Kiến trúc agent theo LangGraph (có trạng thái rõ ràng)
- Ghi nhớ lịch sử hội thoại
- Dễ dàng mở rộng thêm công cụ (tools), bộ nhớ, plugins

---

## 🧱 Kiến trúc thư mục

```
src/
├── agent/              # Agent chính sử dụng LangGraph
│   └── langgraph_agent.py
├── llm/                # Giao tiếp với LLM của Google
│   └── google_llm.py
├── memory/             # Ghi nhớ hội thoại (tùy chọn)
├── tools/              # Tool bổ sung (tùy chọn)
├── config/             # Cấu hình (nếu cần)
├── main.py             # Điểm chạy chính
tests/                  # Unit tests
.env                    # Biến môi trường
```

---

## 📦 Cài đặt

### 1. Clone và cài thư viện

```bash
git clone https://github.com/your-user/ai-agent-langgraph.git
cd ai-agent-langgraph
poetry install
```

### 2. Thiết lập biến môi trường

Tạo file `.env` và thêm:

```
GOOGLE_API_KEY=your_google_api_key
```

> Lấy API Key tại: https://makersuite.google.com/app/apikey

---

## ▶️ Chạy Agent

```bash
poetry run python src/main.py
```

Ví dụ sử dụng:

```
Bạn: Xin chào
AI: Chào bạn! Tôi có thể giúp gì hôm nay?
```

---

## 🧠 Công nghệ sử dụng

- [LangGraph](https://github.com/langchain-ai/langgraph) – xây dựng luồng agent
- [Google Generative AI](https://ai.google.dev/) – mô hình Gemini / PaLM
- [LangChain](https://github.com/langchain-ai/langchain) – tích hợp tools, memory
- [Poetry](https://python-poetry.org/) – quản lý gói

---

## 🛠 Mở rộng

- ➕ Thêm memory bằng FAISS hoặc SQLite
- 🔍 Kết nối công cụ tìm kiếm (Google, DuckDuckGo, Serper...)
- 🧩 Tạo thêm node LangGraph để xử lý phân nhánh (ví dụ: phân loại đầu vào, phân tích cú pháp, gọi API...)

---

## 📄 License

MIT License © 2025 Your Name
