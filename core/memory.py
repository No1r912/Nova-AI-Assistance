from core.utils import load_json, save_json
from core.config import MEMORY_FILE

memory = load_json(MEMORY_FILE, {})

def save():
    save_json(MEMORY_FILE, memory)





# profile management functions
def get(key):
    return memory.get(key)


def set_profile(key, value):
    if "profile" not in memory:
        memory["profile"] = {}


    memory["profile"][key] = value
    save()


def get_profile(key):
    return memory.get("profile", {}).get(key)






# preference management functions
def set_preference(key, value):
    if "preferences" not in memory:
        memory["preferences"] = {}

    memory["preferences"][key] = value
    save()

def get_preferences():
    return memory.get("preferences", {})


def add_to_list(category, key, value):
    if category not in memory:
        memory[category] = {}

    if key not in memory[category]:
        memory[category][key] = []

    if not any(str(item).casefold() == str(value).casefold() for item in memory[category][key]):
        memory[category][key].append(value)

    save()






#goal management functions
def add_goal(goal_type, goal):
    if "goals" not in memory:
        memory["goals"] = {}

    if goal_type not in memory["goals"]:
        memory["goals"][goal_type] = []

    if not any(item.casefold() == goal.casefold() for item in memory["goals"][goal_type]):
        memory["goals"][goal_type].append(goal)

    save()

def complete_goal(goal):
    goals = memory.get("goals", {})

    if goal in goals.get("short_term", []):
        goals["short_term"].remove(goal)

    if goal in goals.get("long_term", []):
        goals["long_term"].remove(goal)

    goals.setdefault("completed", [])

    if goal not in goals["completed"]:
        goals["completed"].append(goal)

    save()




#project management functions
def create_project(name):
    if "projects" not in memory:
        memory["projects"] = {}

    if name not in memory["projects"]:
        memory["projects"][name] = {
            "description": "",
            "status": "Planning",
            "language": "",
            "tasks": [],
            "completed": [],
            "notes": []
        }

    save()

def update_project(name, key, value):

    create_project(name)

    memory["projects"][name][key] = value

    save()

def add_project_task(name, task):
    create_project(name)

    if task not in memory["projects"][name]["tasks"]:
        memory["projects"][name]["tasks"].append(task)

    save()

def complete_project_task(name, task):
    create_project(name)

    if task in memory["projects"][name]["tasks"]:
        memory["projects"][name]["tasks"].remove(task)

    if task not in memory["projects"][name]["completed"]:
        memory["projects"][name]["completed"].append(task)

    save()

def add_project_note(name, note):
    create_project(name)

    memory["projects"][name]["notes"].append(note)

    save()







#summary management functions
def add_summary(summary):
    if "conversation_summaries" not in memory:
        memory["conversation_summaries"] = []

    memory["conversation_summaries"].append(summary)
    save()

def get_summaries():
    return memory.get("conversation_summaries", [])

def trim_summaries(limit=20):
    if "conversation_summaries" not in memory:
        return

    if len(memory["conversation_summaries"]) > limit:
        memory["conversation_summaries"] = \
            memory["conversation_summaries"][-limit:]

    save()





#fact management functions
def add_important_fact(fact):
    if "important_facts" not in memory:
        memory["important_facts"] = []

    if not any(item.casefold() == fact.casefold() for item in memory["important_facts"]):
        memory["important_facts"].append(fact)

    save()

def get_important_facts():
    return memory.get("important_facts", [])

def remove_important_fact(fact):
    """Forget an important fact using case-insensitive exact matching."""
    if "important_facts" not in memory:
        return False

    for saved_fact in memory["important_facts"][:]:
        if saved_fact.casefold() == fact.casefold():
            memory["important_facts"].remove(saved_fact)
            save()
            return True

    return False


def clear_all():
    """Forget all long-term information after an explicit user request."""
    memory.clear()
    save()

def all():
    return memory
