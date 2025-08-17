import speech_recognition as sr

language='ru_RU' 

def recognise(filename):
    r = sr.Recognizer() 

    with sr.AudioFile(filename) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text,language=language)
            print('Расшифровка аудио в текст ...')
            print(text)
            return text
        except:
            print('Извините.. попробуйте снова...')
            return "Извините.. попробуйте снова..."
        