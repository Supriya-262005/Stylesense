import os
import json
from groq import Groq

# Initialize Groq client
# We will use a try-except block to handle missing API keys gracefully for now
try:
    api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=api_key) if api_key else None
except Exception as e:
    print(f"Groq Init Error: {e}")
    client = None

def get_recommendations(profile):
    """
    Generates recommendations using Groq based on the user profile.
    Profile includes: shape, skin_tone, gender
    """
    if not client:
        return mock_response(profile)

    prompt = f"""
    You are a high-end fashion stylist. Create a personalized style guide for a user with these attributes:
    - Face Shape: {profile.get('shape')}
    - Skin Tone: {profile.get('skin_tone')}
    - Gender: {profile.get('gender', 'Unspecified')}

    Provide recommendations in strict JSON format with the following structure:
    {{
        "outfits": [
            {{"name": "Outfit Name", "description": "Brief description", "keywords": "search terms for google shopping"}},
            ... (3 recommendations: 1 Casual, 1 Formal, 1 Party)
        ],
        "hair": [
            {{"style": "Hairstyle Name", "description": "Why it suits them", "keywords": "hairstyle search terms"}}
            ... (2 recommendations)
        ],
        "accessories": [
            {{"name": "Accessory Name", "description": "Why it suits them", "keywords": "accessory search terms"}}
            ... (2 recommendations)
        ]
    }}
    Do not include any markdown formatting, just the raw JSON string.
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful fashion assistant that outputs JSON only."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            temperature=0.7,
        )
        content = completion.choices[0].message.content
        # Clean up if model returns markdown ticks
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"AI Error: {e}")
        return mock_response(profile)

def mock_response(profile):
    """Fallback if API fails or key missing"""
    return {
        "outfits": [
            {"name": "Classic Chic", "description": "A safety fallback outfit.", "keywords": "classic white shirt blue jeans"},
            {"name": "Evening Elegance", "description": "A formal option.", "keywords": "black evening dress or suit"}
        ],
        "hair": [
             {"style": "Classic Cut", "description": "Works for everyone.", "keywords": "classic haircut"}
        ],
        "accessories": [
             {"name": "Watch", "description": "Timeless.", "keywords": "classic analog watch"}
        ]
    }
