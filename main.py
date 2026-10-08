import argparse

from core.conversation import respond
from core.config import AI_NAME
from core.logger import info, error

from voice.listen import listen
from voice.speak import speak



# =========================
# Text Mode
# =========================

def text_mode():

    print(f"{AI_NAME} chat started. Type your messages; Nova will speak its replies. Type /help for controls.")

    while True:

        try:

            user = input("\nYou: ").strip()


            if user.lower() in [
                "exit",
                "quit",
                "shutdown",
                "goodbye",
                "/exit"
            ]:

                print(f"{AI_NAME}: Goodbye!")
                break


            if not user:
                continue


            answer = respond(user)


            print(
                f"{AI_NAME}: {answer}"
            )

            speak(answer)


        except Exception as e:

            error(
                f"Text mode error: {e}"
            )

            print(
                "Error:",
                e
            )



# =========================
# Voice Mode
# =========================

def voice_mode():

    print(f"{AI_NAME} voice chat started. Speak naturally; say 'exit voice chat' to stop.")
    speak("Voice chat is ready. What would you like to talk about?")



    while True:

        try:


            user = listen()


            if not user:

                continue



            print(
                "You:",
                user
            )

            if user.lower().strip() in {
                "exit", "quit", "stop", "goodbye", "exit voice chat", "stop voice chat"
            }:
                farewell = "Voice chat closed. Talk to you later."
                print(f"{AI_NAME}: {farewell}")
                speak(farewell)
                break

            answer = respond(user)


            print(
                f"{AI_NAME}: {answer}"
            )


            speak(answer)



        except KeyboardInterrupt:

            print(
                "\nStopping Nova..."
            )

            break



        except Exception as e:

            error(
                f"Voice mode error: {e}"
            )

            print(
                "Error:",
                e
            )



def main():

    parser = argparse.ArgumentParser(description="Run the Nova local assistant.")
    parser.add_argument("--text", action="store_true", help="run the console chat instead of the desktop app")
    parser.add_argument("--gui", action="store_true", help="run the desktop app")
    args = parser.parse_args()

    info(
        f"{AI_NAME} starting..."
    )
    if args.text:
        text_mode()
        return

    from ui.nova_gui import run as run_gui
    run_gui()



if __name__ == "__main__":

    main()
