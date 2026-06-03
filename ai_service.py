import google.generativeai as genai
from openai import OpenAI
from config_manager import load_config

def generate_ai_response(user_message: str) -> str:
    config = load_config()
    provider = config.get("ai_provider", "gemini").lower()
    system_prompt = config.get("system_prompt", "")
    
    if provider == "gemini":
        api_key = config.get("gemini_api_key", "").strip()
        model_name = config.get("gemini_model", "gemini-1.5-flash").strip()
        
        if not api_key:
            return "Gemini API key is missing. Please configure it in the dashboard."
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt if system_prompt else None
            )
            response = model.generate_content(user_message)
            return response.text.strip() if (response and response.text) else "AI returned an empty response."
        except Exception as e:
            return f"Gemini API Error: {str(e)}"
            
    elif provider == "openai":
        api_key = config.get("openai_api_key", "").strip()
        model_name = config.get("openai_model", "gpt-4o").strip()
        
        if not api_key:
            return "OpenAI API key is missing. Please configure it in the dashboard."
            
        try:
            client = OpenAI(api_key=api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=500
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            return "AI returned an empty response."
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"
            
    return "Unknown AI provider configured."
