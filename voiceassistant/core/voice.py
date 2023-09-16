import whisper
from django.conf import settings

model = whisper.load_model(str(settings.BASE_DIR) + "/medium.pt")

def get_text_from_audio(audio):
    audio_path = str(settings.BASE_DIR)  + audio
    translate_output = model.transcribe(audio_path, task = 'translate')
    return translate_output