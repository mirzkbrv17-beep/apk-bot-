import asyncio, os
from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get("/")
async def health(): return {"status":"ok","service":"Ultimate APK Platform"}
async def start_health_server():
    config=uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")), log_level="warning")
    server=uvicorn.Server(config)
    asyncio.create_task(server.serve())
