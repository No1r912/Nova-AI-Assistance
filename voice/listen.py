from ai.whisper_client import transcribe
from voice.audio import record_audio


# =========================
# Listen Function
# =========================

def listen():

    try:

        # Record microphone
        audio_file = record_audio()


        if not audio_file:

            print("No audio recorded.")
            return None



        print("🧠 Recognizing...")


        final_text = transcribe(audio_file, language="en")

        if not final_text:
            return None


        # Remove duplicate sentences
        words = final_text.split()


        cleaned = []

        for word in words:

            if not cleaned or word != cleaned[-1]:

                cleaned.append(word)


        final_text = " ".join(cleaned)



        print(
            "Final text:",
            repr(final_text)
        )


        return final_text



    except Exception as e:

        print(
            "Listen error:",
            e
        )

        return None
