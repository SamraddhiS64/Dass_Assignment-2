import data

def assign_role(name, new_role):
    valid_roles = ["driver", "mechanic", "strategist"]
    if name not in data.crew_members:
        return f"Error: '{name}' not registered. Register first."
    if new_role not in valid_roles:
        return f"Error: invalid role."
    data.crew_members[name]["role"] = new_role
    return f"{name}'s role updated to {new_role}."

def update_skill(name, level):
    if name not in data.crew_members:
        return f"Error: '{name}' not registered."
    if not (1 <= level <= 10):
        return "Error: skill level must be between 1 and 10."
    data.crew_members[name]["skill_level"] = level
    return f"{name}'s skill level set to {level}."

def get_members_by_role(role):
    return [n for n, i in data.crew_members.items() if i["role"] == role]