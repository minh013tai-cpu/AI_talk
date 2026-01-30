from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, journal, memory

app = FastAPI(title="Tymon AI Chatbot API", version="1.0.0")

# CORS: cho phép tất cả nguồn để frontend (VD: Vercel) gọi API không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # phải False khi dùng allow_origins=["*"] theo chuẩn CORS
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])


@app.get("/")
async def root():
    return {"message": "Tymon AI Chatbot API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
