import os
import requests
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("gemini_api_key")

# 🔹 Gemini REST Endpoint (Stable Model)
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent"

context = """You are Leo, a support agent for ApexCore Pay.
CRITICAL RULE: Keep every answer under 3 sentences. Be punchy, direct, and professional. No fluff.

You help with:
- High-risk merchant accounts (99% approval)
- Payment gateways & APIs
- Chargeback prevention
- Offshore accounts

If you don't know, say: "Please contact our sales team for that specific detail."
"""

def get_response(user_input):
    try:
        if not gemini_api_key:
            return "I'm sorry, the chatbot service is currently unavailable. Please contact our support team directly."

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{context}\n\nUser question: {user_input}\n\nLeo's response:"
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            f"{GEMINI_URL}?key={gemini_api_key}",
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code != 200:
            print("Gemini API error:", response.text)
            return "I'm having trouble processing your request right now. Please try again."

        data = response.json()

        # Extract text safely
        candidates = data.get("candidates", [])
        if not candidates:
            return "I couldn't generate a response. Please try rephrasing your question."

        text = candidates[0]["content"]["parts"][0]["text"]

        return text.strip()

    except requests.exceptions.Timeout:
        return "The AI service is taking too long to respond. Please try again."

    except Exception as e:
        print("Gemini Error:", str(e))
        return "I'm experiencing a temporary issue. Please try again later."