import pyttsx3
e = pyttsx3.init()
for v in e.getProperty('voices'):
    print(f"ID: {v.id}\nName: {getattr(v, 'name', '')}\nLangs: {getattr(v, 'languages', '')}\n-------")
