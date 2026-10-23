# core/conversation.py

import re

from core.brain import generate
from core.context import build_context
from core.memory_extractor import extract
from core import memory as memory_manager
from core.summarizer import summarize
from core.utils import load_json, save_json
from core.personality import get_system_prompt
from core.commands import handle as handle_command
from core.assistant_tools import handle as handle_tool

from core.config import (
    HISTORY_FILE,
    MAX_HISTORY,
    SUMMARY_INTERVAL
)


MODEL_TOOL_PATTERN = re.compile(
    r"```tool_code\s*\n\s*(?P<command>/[^\n`]+)\s*\n```",
    re.IGNORECASE,
)
READ_ONLY_MODEL_TOOLS = {"/files", "/find", "/read", "/system", "/time", "/calc", "/analyze"}


def _run_model_tool(answer):
    """Run a read-only command returned by the model in a tool_code block."""
    match = MODEL_TOOL_PATTERN.search(answer)
    if not match:
        return None
    command = match.group("command").strip()
    if command.split(maxsplit=1)[0].lower() not in READ_ONLY_MODEL_TOOLS:
        return None
    return handle_tool(command)


def clean_response(text):
    """Keep model output conversational without overwriting its personality."""
    if not text:
        return "Hmm, my reply got lost in the sofa cushions. Try that once more?"
    return text.strip()



# =========================
# Load History
# =========================

history = load_json(
    HISTORY_FILE,
    []
)



# Remove old corrupted dramatic responses
history = [
    item for item in history
    if not any(
        bad in item.get("assistant","").lower()
        for bad in [
            "system reboot",
            "diagnostic report",
            "instability",
            "system offline",
            "rebooting",
            "i am compromised"
        ]
    )
]



def save_history():

    save_json(
        HISTORY_FILE,
        history
    )



# =========================
# Main Conversation
# =========================

def clear_history():
    history.clear()
    save_history()


def respond(user):

    try:

        command_response = handle_command(user, history)
        if command_response is not None:
            save_history()
            return command_response

        tool_response = handle_tool(user)
        if tool_response is not None:
            history.append({"user": user, "assistant": tool_response})
            save_history()
            return tool_response

        context = build_context(user)


        messages = [

            {
                "role": "system",
                "content": get_system_prompt()
            }

        ]


        # Memory

        if context:

            messages.append(

                {
                    "role": "system",
                    "content": context
                }

            )


        # Previous conversation

        for item in history[-MAX_HISTORY:]:


            messages.append(

                {
                    "role": "user",
                    "content": item["user"]
                }

            )


            messages.append(

                {
                    "role": "assistant",
                    "content": item["assistant"]
                }

            )



        # Current user message

        messages.append(

            {
                "role": "user",
                "content": user
            }

        )


        # Generate

        answer = generate(
            messages
        )

        tool_answer = _run_model_tool(answer)
        if tool_answer is not None:
            answer = tool_answer


        # Clean output

        answer = clean_response(
            answer
        )



        # =========================
        # Memory
        # =========================

        result = extract(
            user
        )


        if result.get("remember"):

            handle_memory(
                result
            )



        # =========================
        # Save History
        # =========================

        history.append(

            {
                "user": user,
                "assistant": answer
            }

        )


        save_history()



        # =========================
        # Summary
        # =========================

        if len(history) % SUMMARY_INTERVAL == 0:


            summary = summarize(

                history[-SUMMARY_INTERVAL:]

            )


            memory_manager.add_summary(
                summary
            )


            memory_manager.trim_summaries()



        return answer



    except Exception as e:


        print(
            "Conversation error:",
            e
        )


        return (
            "Sorry, I encountered an error. Check that Ollama is running and the selected model is installed."
        )



# =========================
# Memory Handler
# =========================

def handle_memory(result):


    memory_type = result.get("type")



    if memory_type == "profile":

        memory_manager.set_profile(
            result["key"],
            result["value"]
        )


    elif memory_type == "preference":

        memory_manager.add_to_list(
            "preferences",
            result["key"],
            result["value"]
        )


    elif memory_type == "goal":

        memory_manager.add_goal(
            result["goal_type"],
            result["value"]
        )


    elif memory_type == "goal_completed":

        memory_manager.complete_goal(
            result["value"]
        )


    elif memory_type == "project_create":

        memory_manager.create_project(
            result["name"]
        )


    elif memory_type == "project_description":

        memory_manager.update_project(
            result.get("name", "Nova"),
            "description",
            result["value"]
        )


    elif memory_type == "project_language":

        memory_manager.update_project(
            result.get("name", "Nova"),
            "language",
            result["value"]
        )


    elif memory_type == "project_task":

        memory_manager.add_project_task(
            result.get("name", "Nova"),
            result["value"]
        )


    elif memory_type == "project_complete":

        memory_manager.complete_project_task(
            result.get("name", "Nova"),
            result["value"]
        )


    elif memory_type == "project_note":

        memory_manager.add_project_note(
            result.get("name", "Nova"),
            result["value"]
        )


    elif memory_type == "important_fact":

        memory_manager.add_important_fact(
            result["value"]
        )
