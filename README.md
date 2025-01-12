# Setup

## PyCharm

1. Mark `src` as sources root
2. Create "user-data" in the project root.
3. Create a blank user file. It's JSON format, see an example for an en-ru learning file.

    ```json
    {
      "language": "en",
      "secondLanguage": "ru",
      "root": {
        
      }
    }
    ```

4. Create the ".env" file with your keys.

    ```
    OPENAI_API_KEY=xxxxx
    SPEECH_KEY=xxxxx
    SPEECH_REGION=xxxxx
    GOOGLE_API_KEY=xxxxx
    ```

# Run

Run ui/MainWindow.

Specify "../../user-data/<your user json>" as the argument.
