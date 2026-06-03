import os

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

DEFAULT_CONFIG = {
    "instagram_access_token": "",
    "instagram_account_id": "",
    "webhook_verify_token": "insta_bot_verify_token_123",
    "ai_provider": "gemini",
    "gemini_api_key": "",
    "gemini_model": "gemini-1.5-flash",
    "openai_api_key": "",
    "openai_model": "gpt-4o",
    "system_prompt": "You are a helpful and polite Instagram virtual assistant. Keep your responses friendly, concise (under 2-3 sentences), and suitable for direct messaging. Do not use hashtags unless asked.",
    "ngrok_auth_token": "",
    "use_auto_tunnel": "false"
}

def load_config():
    if not os.path.exists(ENV_FILE):
        save_config(DEFAULT_CONFIG)
        return get_typed_config(DEFAULT_CONFIG)

    config = {}
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                parts = line.split("=", 1)
                key = parts[0].strip().lower()
                val = parts[1].strip()
                
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                
                val = val.replace("\\n", "\n").replace("\\r", "\r")
                config[key] = val
    except Exception as e:
        print(f"Error reading .env: {e}")

    updated = False
    for k, v in DEFAULT_CONFIG.items():
        if k not in config:
            config[k] = v
            updated = True
            
    if updated:
        save_config(config)

    return get_typed_config(config)

def save_config(config_data):
    try:
        existing_lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        
        env_map = {}
        for k, v in DEFAULT_CONFIG.items():
            env_key = k.upper()
            val = config_data.get(k, v)
            if isinstance(val, bool):
                val = "true" if val else "false"
            elif val is None:
                val = ""
            
            val_str = str(val).replace("\n", "\\n").replace("\r", "\\r")
            env_map[env_key] = val_str

        updated_keys = set()
        new_lines = []
        
        for line in existing_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                parts = stripped.split("=", 1)
                env_key = parts[0].strip()
                if env_key in env_map:
                    new_lines.append(f'{env_key}="{env_map[env_key]}"\n')
                    updated_keys.add(env_key)
                    continue
            new_lines.append(line)

        for env_key, val in env_map.items():
            if env_key not in updated_keys:
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines.append("\n")
                new_lines.append(f'{env_key}="{val}"\n')

        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
            
        for env_key, val in env_map.items():
            os.environ[env_key] = val
            
        return True
    except Exception as e:
        print(f"Error saving to .env: {e}")
        return False

def get_typed_config(config):
    typed_config = {}
    for k, v in config.items():
        if k == "use_auto_tunnel":
            typed_config[k] = str(v).lower() in ("true", "1", "yes")
        else:
            typed_config[k] = v
    return typed_config
