import requests
from config_manager import load_config

def send_instagram_message(recipient_id: str, text: str) -> dict:
    config = load_config()
    access_token = config.get("instagram_access_token", "").strip()
    
    if not access_token:
        return {"success": False, "error": "Instagram Access Token is missing."}
        
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": access_token}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    
    try:
        response = requests.post(url, json=payload, params=params, timeout=10)
        res_json = response.json()
        if response.status_code == 200:
            return {"success": True, "data": res_json}
        
        err_msg = res_json.get("error", {}).get("message", "Unknown Graph API Error")
        return {"success": False, "error": f"API Error ({response.status_code}): {err_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_instagram_user_profile(user_id: str) -> dict:
    config = load_config()
    access_token = config.get("instagram_access_token", "").strip()
    
    if not access_token:
        return {"success": False, "error": "Instagram Access Token missing."}
        
    url = f"https://graph.facebook.com/v17.0/{user_id}"
    params = {
        "fields": "name,username",
        "access_token": access_token
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": response.json().get("error", {}).get("message", "Profile fetch failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}
