import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

def consultar_qwen(prompt: str) -> str:
    if not QWEN_API_KEY:
        return "Erro: Chave da API não encontrada no .env."

    # Mantemos a URL correta do OpenRouter que testamos
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Projeto Gorila"
    }
    
    payload = {
        # O modelo exato que você validou no OpenClaude
        "model": "qwen/qwen3.6-plus:free", 
        "messages": [
            {"role": "system", "content": "Você é um assistente fitness integrado ao aplicativo Projeto Gorila. Responda de forma curta e direta, focado em musculação e hipertrofia."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            return f"Erro na IA (Status {response.status_code}): {response.text}"
            
        dados = response.json()
        return dados["choices"][0]["message"]["content"]
    except Exception as e:
        raw_text = response.text if 'response' in locals() else 'Sem resposta do servidor'
        return f"Falha na comunicação: {str(e)} | Resposta Bruta: {raw_text}"