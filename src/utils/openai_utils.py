from dotenv import load_dotenv
from openai import OpenAI

MODEL_BASIC = "gpt-3.5-turbo-1106"
MODEL_HEAVY = "gpt-4-1106-preview"


def stream_chat_completion(client: OpenAI, model_name: str, messages: list, temperature: float, stream_callback) -> str:
    # Initialize the result string
    result = ""
    # Initialize the token count
    chunk_count = 0

    # Create the chat completion stream
    stream = client.chat.completions.create(
        model=model_name,
        messages=messages,
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


def do_main():
    load_dotenv()
    openai_client = OpenAI()
    story = stream_chat_completion(openai_client, MODEL_BASIC, [
        {
            "role": "user",
            "content": "Write a sentence about electricity and diamonds."
        }
    ], 1, lambda x: print(x))
    print(story)


if __name__ == '__main__':
    do_main()
