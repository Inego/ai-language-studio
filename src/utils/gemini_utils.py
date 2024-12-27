from typing import get_args

from google import genai
from google.genai import types
from google.genai.types import HarmCategory

_MODEL = 'gemini-2.0-flash-exp'


def stream_chat_completion(client: genai.Client, use_heavy_model: bool, system_message: str, instruct: str,
                           temperature: float, stream_callback) -> str:
    # Initialize the result string
    result = ""
    # Initialize the token count
    chunk_count = 0

    for chunk in client.models.generate_content_stream(
            model=_MODEL,
            contents=instruct,
            config=types.GenerateContentConfig(
                safety_settings=[types.SafetySetting(
                    category=c,
                    threshold='OFF',
                ) for c in get_args(HarmCategory)[1:]],
                temperature=0.0
            )
    ):
        # Append the content to the result string
        result += chunk.text
        # Update the token count
        chunk_count += 1
        # Call the stream_callback with the current token count
        stream_callback(chunk_count)

    return result
