from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

MODELS = {
    # "🖥️ Gemma 3 (Local)": ("ollama", "gemma3:1b"),
    "⚡ Llama 3.3 70B (Groq)": ("groq", "llama-3.3-70b-versatile"),
    "⚡ Llama 3.1 8B (Groq)": ("groq", "llama-3.1-8b-instant"),
    "✨ Gemini 2.5 Flash": ("gemini", "gemini-2.5-flash"),
}


def get_llm(model_name):
    provider, model_id = MODELS[model_name]
    if provider == "ollama":
        print(model_id)
        return ChatOllama(model=model_id, temperature=0)
    elif provider == "groq":
        print(model_id)
        return ChatGroq(model=model_id, temperature=0)
    elif provider == "gemini":
        print(model_id)
        return ChatGoogleGenerativeAI(model=model_id, temperature=0)
