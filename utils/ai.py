import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def get_safety_advice(user_message):

    if not API_KEY:
        return "Gemini API key is not configured."

    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options=types.HttpOptions(
                api_version="v1"
            )
        )

        prompt = f"""
You are SafeHer AI, a personal safety assistant.

User situation:
{user_message}

Give calm, practical safety guidance.

Rules:
1. Prioritize immediate safety.
2. Give 3 to 5 simple practical steps.
3. If the user is in immediate danger, advise contacting
   local emergency services or a trusted person.
4. Do not give dangerous or illegal instructions.
5. Keep the response simple and easy to understand.
"""

        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        return interaction.output_text

    except Exception as error:
        return f"AI service error: {error}"