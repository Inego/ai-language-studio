import base64
import time


def encode_by_time(n=0):
    # Ensure n is within the expected range
    if not (0 <= n <= 1_000_000):
        raise ValueError("n must be between 0 and 1,000,000 inclusive")

    # Get the current epoch time in milliseconds
    current_time_millis = int(time.time() * 1000)

    # Multiply by 1,000,000 and add n
    result = current_time_millis * 1_000_000 + n

    # Convert the result to bytes
    result_bytes = result.to_bytes((result.bit_length() + 7) // 8, byteorder='big')

    # Encode the bytes to a base64 string
    encoded_string = base64.urlsafe_b64encode(result_bytes).decode('utf-8').rstrip('=')

    return encoded_string
