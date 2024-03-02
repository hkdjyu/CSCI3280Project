import os
import threading
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

class AudioTextConverter:
    def __init__(self):
        self.r = sr.Recognizer()

    def transcribe_audio(self, path):
        """Recognize speech in the audio file."""
        with sr.AudioFile(path) as source:
            audio_listened = self.r.record(source)
            try:
                text = self.r.recognize_google(audio_listened)
                return text
            except sr.UnknownValueError as e:
                print("Error:", str(e))
                return ""

    def transcribe_audio_threaded(self, path, callback):
        """Recognize speech in the audio file in a separate thread."""
        def transcribe():
            result = self.transcribe_audio(path)
            callback(result)
        thread = threading.Thread(target=transcribe)
        thread.start()

    def get_large_audio_transcription_on_silence(self, path, callback_complete=None, callback_chunk=None):
        """Split the large audio file into chunks and apply speech recognition on each chunk."""
        def split_and_transcribe():
            sound = AudioSegment.from_file(path)
            chunks = split_on_silence(sound,
                                      min_silence_len=500,
                                      silence_thresh=sound.dBFS - 14,
                                      keep_silence=500)
            folder_name = "audio-chunks"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            whole_text = ""
            for i, audio_chunk in enumerate(chunks, start=1):
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                text = self.transcribe_audio(chunk_filename)
                text = f"{text.capitalize()}. "
                # print(chunk_filename, ":", text)
                whole_text += text
                if callback_chunk:
                    callback_chunk(text, i, len(chunks))
            if callback_complete:
                callback_complete(whole_text)

        thread = threading.Thread(target=split_and_transcribe)
        thread.start()
