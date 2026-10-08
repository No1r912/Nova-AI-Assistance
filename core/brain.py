# core/brain.py

from ai.ollama_client import generate as ollama_generate


def generate(messages):
    """
    Send messages to the local language model
    and return the generated response.
    """

    try:

        response = ollama_generate(
            messages
        )

        if response:

            return response.strip()


        return (
            "I could not generate a response."
        )


    except Exception as e:

        print(
            "Brain error:",
            e
        )

        return (
            "Sorry, I encountered an error while generating a reply."
        )
