import os
import httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="Sora 2 Free Proxy")

# 从环境变量获取配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# 设置你的自定义访问密码，部署时在环境变量里设置
MY_SECRET_KEY = os.getenv("MY_SECRET_KEY", "default_password") 

# 定义请求数据格式
class SoraRequest(BaseModel):
    prompt: str
    size: str = "1080x1920" # 默认竖屏
    quality: str = "standard"

@app.get("/")
def home():
    return {"status": "Sora Proxy is running"}

@app.post("/generate")
async def generate_video(request: SoraRequest, access_token: str = Header(None)):
    """
    封装后的生成接口
    """
    # 1. 安全检查：验证你的自定义密码
    if access_token != MY_SECRET_KEY:
        raise HTTPException(status_code=403, detail="密码错误，无法访问")

    # 2. 准备发送给 OpenAI 的数据
    # 注意：请根据 Sora 2 官方文档确认最终的 endpoint 和 model 名称
    url = "https://api.openai.com/v1/videos/generations" 
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sora-2.0",  # 假设模型名为 sora-2.0
        "prompt": request.prompt,
        "size": request.size,
        "quality": request.quality
    }

    # 3. 异步调用 OpenAI (设置较长的超时时间，因为视频生成很慢)
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status() # 检查是否有错误
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": "OpenAI API Error", "details": e.response.text}
        except Exception as e:
            return {"error": "Server Error", "details": str(e)}