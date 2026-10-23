"""Extract durable, user-provided details from natural conversation."""

import re


def _value(match):
    return match.group(1).strip(" .,!?")


def _match(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and _value(match):
            return _value(match)
    return None


def extract(text):
    """Return one high-confidence memory candidate, or ``remember: False``."""
    text = " ".join(text.strip().split())
    if not text:
        return {"remember": False}

    # Explicit opt-out wins over every automatic pattern below. This keeps
    # natural chat from becoming a surprise diary.
    if re.search(r"\b(?:don't|do not|dont) remember\b", text, re.IGNORECASE):
        return {"remember": False}

    name = _match(text, (r"\bmy name is\s+(.+)$", r"\bcall me\s+(.+)$"))
    if name:
        return {"remember": True, "type": "profile", "key": "name", "value": name}

    location = _match(text, (r"\bI(?:'m| am) from\s+(.+)$", r"\bI live in\s+(.+)$"))
    if location:
        return {"remember": True, "type": "profile", "key": "location", "value": location}

    age = _match(text, (r"\bI(?:'m| am)\s+(\d{1,3})\s+years old\b",))
    if age:
        return {"remember": True, "type": "profile", "key": "age", "value": int(age)}

    preference_patterns = (
        ("likes", (r"\bI (?:really )?like\s+(.+)$", r"\bI love\s+(.+)$")),
        ("dislikes", (r"\bI (?:don't|do not) like\s+(.+)$", r"\bI hate\s+(.+)$")),
        ("interests", (r"\bI(?:'m| am) interested in\s+(.+)$", r"\bI(?:'m| am) into\s+(.+)$")),
        ("favorite_language", (r"\bmy favou?rite (?:programming )?language is\s+(.+)$",)),
        ("favorite_editor", (r"\bmy (?:code )?editor is\s+(.+)$",)),
    )
    for key, patterns in preference_patterns:
        value = _match(text, patterns)
        if value:
            return {"remember": True, "type": "preference", "key": key, "value": value}

    goal = _match(text, (r"\bI want to\s+(.+)$", r"\bI(?:'m| am) planning to\s+(.+)$"))
    if goal and any(word in goal.lower() for word in ("learn", "build", "create", "finish", "study", "improve", "develop")):
        return {"remember": True, "type": "goal", "goal_type": "short_term", "value": goal}

    project = _match(text, (r"\bI(?:'m| am) working on\s+(.+)$",))
    if project:
        return {"remember": True, "type": "project_create", "name": project}

    fact = _match(text, (r"\bremember that\s+(.+)$",))
    if fact:
        return {"remember": True, "type": "important_fact", "value": fact}

    return {"remember": False}
