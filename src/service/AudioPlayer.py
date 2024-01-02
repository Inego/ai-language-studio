import os

from PyQt5.QtCore import QBuffer, QByteArray
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from azure.cognitiveservices.speech import SpeechSynthesizer, SpeechConfig, SpeechSynthesisOutputFormat


class AudioPlayer:
    def __init__(self, openai_client, parent):
        self.openai_client = openai_client
        self.cache = {}
        self.speech_synthesizers = {}

        self.media_player = QMediaPlayer()
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        self.audio_buffer = QBuffer()

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.LoadedMedia:
            # The media is loaded and ready to be played
            self.media_player.play()

    def play(self, voice, utterance):
        audio_bytes = self.get_or_retrieve(voice, utterance)

        self.audio_buffer.close()
        self.audio_buffer = QBuffer()
        self.audio_buffer.setData(QByteArray(audio_bytes))
        self.audio_buffer.open(QBuffer.ReadOnly)
        media_content = QMediaContent()
        self.media_player.setMedia(media_content, self.audio_buffer)

    def play_now(self):
        self.media_player.play()

    def get_or_retrieve(self, voice, utterance):
        cache_key = f"{voice}#{utterance}"
        if cache_key not in self.cache:
            self.cache[cache_key] = self.get_audio_bytes(voice, utterance)
        return self.cache[cache_key]

    def get_audio_bytes(self, voice, utterance):
        print(f"Retrieving from {voice}: {utterance}")
        speech_synthesizer = self.get_speech_synthesizer(voice)

        result = speech_synthesizer.speak_text_async(utterance).get()

        print("Done.")
        return result.audio_data

    def get_speech_synthesizer(self, voice):

        result = self.speech_synthesizers.get(voice)
        if result is None:
            speech_config = SpeechConfig(
                subscription=os.environ.get('SPEECH_KEY'),
                region=os.environ.get('SPEECH_REGION')
            )
            speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3)

            speech_config.speech_synthesis_voice_name = voice

            result = SpeechSynthesizer(speech_config=speech_config, audio_config=None)

            self.speech_synthesizers[voice] = result

        return result
