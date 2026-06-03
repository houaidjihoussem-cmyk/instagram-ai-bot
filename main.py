import os
import sys
import io
from datetime import datetime
from collections import deque
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pyngrok import ngrok, conf

from config_manager import load_config, save_config
from ai_service import generate_ai_response
from instagram_api import send_instagram_message

# Unicode output fix for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logs_buffer = deque(maxlen=50)
ngrok_tunnel_url = None

class SettingsPayload(BaseModel):
    instagram_access_token: str
    instagram_account_id: str
    webhook_verify_token: str
    ngrok_auth_token: str
    use_auto_tunnel: bool
    ai_provider: str
    gemini_model: str
    openai_model: str
    gemini_api_key: str
    openai_api_key: str
    system_prompt: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ngrok_tunnel_url
    config = load_config()
    
    if config.get("use_auto_tunnel") and config.get("ngrok_auth_token"):
        try:
            print("Configuring ngrok...")
            conf.get_default().auth_token = config.get("ngrok_auth_token").strip()
            
            print("Starting ngrok tunnel on port 8000...")
            tunnel = ngrok.connect(8000)
            ngrok_tunnel_url = tunnel.public_url
            print(f"[INFO] Ngrok tunnel online: {ngrok_tunnel_url}")
            print(f"[INFO] Webhook URL for FB Portal: {ngrok_tunnel_url}/webhook")
        except Exception as e:
            print(f"[WARNING] Failed to start ngrok tunnel: {e}")
            
    yield
    
    if ngrok_tunnel_url:
        try:
            print("Stopping ngrok tunnel...")
            ngrok.disconnect(ngrok_tunnel_url)
            ngrok.kill()
        except Exception:
            pass

app = FastAPI(title="InstaAI Auto-Responder", lifespan=lifespan)

@app.get("/")
def get_dashboard():
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "dashboard.html")
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="Dashboard not found.", status_code=404)

@app.get("/webhook")
def verify_webhook(request: Request):
    params = request.query_params
    verify_token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    mode = params.get("hub.mode")
    
    config = load_config()
    expected_verify_token = config.get("webhook_verify_token", "insta_bot_verify_token_123")
    
    if mode == "subscribe" and verify_token:
        if verify_token == expected_verify_token:
            print("[SUCCESS] Webhook verified successfully!")
            return Response(content=challenge, media_type="text/plain")
        else:
            print(f"[ERROR] Webhook verification failed. Token mismatch: Got {verify_token}, expected {expected_verify_token}")
            raise HTTPException(status_code=403, detail="Verification token mismatch")
            
    return Response(content="Instagram Webhook Listener is active.", media_type="text/plain")

def process_webhook_event(payload: dict):
    if payload.get("object") != "instagram":
        return
        
    for entry in payload.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            
            message = messaging_event.get("message", {})
            if message.get("is_echo"):
                continue
                
            message_text = message.get("text")
            if not message_text:
                continue
                
            print(f"Incoming DM from {sender_id}: '{message_text}'")
            
            response_text = generate_ai_response(message_text)
            print(f"AI response: '{response_text}'")
            
            api_result = send_instagram_message(sender_id, response_text)
            
            log_entry = {
                "sender_id": sender_id,
                "message_text": message_text,
                "response_text": response_text,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if not api_result.get("success"):
                log_entry["response_text"] += f" (Send Failed: {api_result.get('error')})"
                
            logs_buffer.appendleft(log_entry)

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        background_tasks.add_task(process_webhook_event, payload)
        return {"status": "EVENT_RECEIVED"}
    except Exception as e:
        print(f"Error handling webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

@app.get("/api/settings")
def get_settings():
    return load_config()

@app.post("/api/settings")
def post_settings(payload: SettingsPayload):
    if save_config(payload.dict()):
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Could not save configuration")

@app.get("/api/status")
def get_status():
    config = load_config()
    return {
        "tunnel_url": ngrok_tunnel_url,
        "ig_token_configured": bool(config.get("instagram_access_token")),
        "gemini_configured": bool(config.get("gemini_api_key")),
        "openai_configured": bool(config.get("openai_api_key"))
    }

@app.get("/api/logs")
def get_logs():
    return list(logs_buffer)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
