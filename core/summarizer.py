from ai.ollama_client import generate


SUMMARY_PROMPT = """
Summarize the following conversation.

Keep only important information:
- User preferences
- Goals
- Projects
- Important facts
- Long-term useful information

Do not include:
- Small talk
- Temporary feelings
- Random details

Return a short summary.
"""



def summarize(history):

    conversation = ""


    for item in history:

        conversation += (
            f"User: {item['user']}\n"
            f"Assistant: {item['assistant']}\n\n"
        )


    messages = [
        {
            "role": "system",
            "content": SUMMARY_PROMPT
        },
        {
            "role": "user",
            "content": conversation
        }
    ]


    return generate(messages)