import speech_recognition as sr
import pyttsx3


def speak(message):
    """
    Converts text into speech.
    """

    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()

    except Exception as error:
        print("Text-to-speech error:", error)


def listen_for_voice():
    """
    Listens to the user's microphone
    and converts speech into text.
    """

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("Listening...")

            speak(
                "SafeHer AI is listening. "
                "Please tell me what happened."
            )

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        text = recognizer.recognize_google(
            audio
        )

        return text

    except sr.WaitTimeoutError:

        return "No voice detected."

    except sr.UnknownValueError:

        return "Sorry, I could not understand your voice."

    except sr.RequestError:

        return "Speech recognition service is unavailable."

    except Exception as error:

        return f"Voice error: {error}"