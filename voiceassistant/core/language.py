from googletrans import Translator

def translate(text, dest):
    translator = Translator()

    source = translator.detect(text=text).lang

    if source != dest:
        return translator.translate(text=text, dest=dest).text
    else:
        return text