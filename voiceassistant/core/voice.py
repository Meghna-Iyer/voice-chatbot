import whisper
import base64
from gtts import gTTS
from io import BytesIO
from django.conf import settings

# Model downloaded and stored in project directory [change as whisper.load_model("medium")]
model = whisper.load_model(str(settings.BASE_DIR) + "/medium.pt")


def getTextFromAudio(audio):
    audio_path = str(settings.BASE_DIR)  + audio
    translate_output = model.transcribe(audio_path, task = 'translate')
    return translate_output


def getAudioFromText(text, language):
    tts = gTTS(text= text, lang=language)

    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    audio_data = base64.b64encode(audio_buffer.read()).decode("utf-8")
    return audio_data