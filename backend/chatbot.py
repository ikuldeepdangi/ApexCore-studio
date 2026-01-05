import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

gemini_api_key = os.getenv('gemini_api_key')

# Configure Gemini API
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# UPDATED PROMPT: Strict instruction for short answers
context = """You are Leo, a support agent for ApexCore Pay. 
CRITICAL RULE: Keep every answer under 3 sentences. Be punchy, direct, and professional. No fluff.

You help with:
- High-risk merchant accounts (99% approval)
- Payment gateways & APIs
- Chargeback prevention
- Offshore accounts

If you don't know, say: "Please contact our sales team for that specific detail." """

# Function to get available models (cached)
_available_model = None

def get_available_model():
    """Get the first available model that supports generateContent"""
    global _available_model
    
    if _available_model:
        return _available_model
    
    try:
        # List available models
        models = genai.list_models()
        for model in models:
            # Check if model supports generateContent
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                print(f"Found available model: {model_name}")
                _available_model = model_name
                return model_name
    except Exception as e:
        print(f"Error listing models: {str(e)}")
    
    # Fallback: try common model names
    fallback_models = ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash-exp']
    return fallback_models[0]  # Return first fallback

# Function to get response from Gemini API
def get_response(user_input):
    try:
        if not gemini_api_key:
            return "I'm sorry, the chatbot service is currently unavailable. Please contact our support team directly."
        
        # Get available model name
        model_name = get_available_model()
        print(f"Using model: {model_name}")
        
        # Create the model
        model = genai.GenerativeModel(model_name)
        
        # Create the full prompt
        prompt = f"{context}\n\nUser question: {user_input}\n\nLeo's response:"
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Check if response has text
        if not response.text:
            return "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
        
        print("Gemini response: ", response.text)
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error getting Gemini response: {error_msg}")
        
        # Reset cached model if there's an error
        global _available_model
        _available_model = None
        
        # Try fallback models
        fallback_models = ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
        for fallback_model in fallback_models:
            try:
                print(f"Trying fallback model: {fallback_model}")
                model = genai.GenerativeModel(fallback_model)
                prompt = f"{context}\n\nUser question: {user_input}\n\nLeo's response:"
                response = model.generate_content(prompt)
                if response.text:
                    _available_model = fallback_model
                    return response.text
            except:
                continue
        
        # Provide more helpful error message
        if "404" in error_msg or "not found" in error_msg.lower():
            return "I'm sorry, there's an issue with the AI service configuration. Please contact our support team."
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            return "I'm sorry, there's an authentication issue with the AI service. Please contact our support team."
        else:
            return "I'm sorry, I'm having trouble processing your request right now. Please try again or contact our support team."