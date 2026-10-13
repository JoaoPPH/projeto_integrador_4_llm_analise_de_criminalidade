import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Inicializa o cliente Groq usando a chave do .env
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY não encontrada nas variáveis de ambiente.")
    return Groq(api_key=api_key)