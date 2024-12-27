from typing import Optional

from google import genai
from openai import OpenAI


from state.Dialog import ApiType
from utils import openai_utils, gemini_utils


def stream_chat_completion(
        openai_client: OpenAI,
        gemini_client: genai.Client,
        api_type: ApiType,
        use_heavy_model: bool,
        instruct: str,
        temperature: float,
        stream_callback,
        system_message: Optional[str] = None
) -> str:
    if api_type == ApiType.OPEN_AI:
        return openai_utils.stream_chat_completion(
            openai_client, use_heavy_model, system_message, instruct, temperature, stream_callback)
    elif api_type == ApiType.GEMINI:
        return gemini_utils.stream_chat_completion(
            gemini_client, use_heavy_model, system_message, instruct, temperature, stream_callback)
