from dotenv import load_dotenv
from openai import OpenAI

MODEL_BASIC = "gpt-4o-mini"
MODEL_HEAVY = "gpt-4o-2024-11-20"


def stream_chat_completion(client: OpenAI, use_heavy_model: bool, system_message: str, instruct: str, temperature: float, stream_callback) -> str:
    # Initialize the result string
    result = ""
    # Initialize the token count
    chunk_count = 0

    # Create the chat completion stream
    stream = client.chat.completions.create(
        model=MODEL_HEAVY if use_heavy_model else MODEL_BASIC,
        messages=([
            {"role": "system", "content": system_message}
        ] if system_message else []) + [{"role": "user", "content": instruct}],
        temperature=temperature,
        stream=True,
    )

    # Iterate over the stream
    for chunk in stream:
        # If there is content in the current chunk, process it
        if chunk.choices[0].delta.content is not None:
            # Append the content to the result string
            result += chunk.choices[0].delta.content
            # Update the token count
            chunk_count += 1
            # Call the stream_callback with the current token count
            stream_callback(chunk_count)

    # Return the assembled result string
    return result
