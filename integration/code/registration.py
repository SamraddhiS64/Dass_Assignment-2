import data

def register(name, role):
    if name in data.crew_members:
        return f"Error: '{name}' is already registered."
    valid_roles = ["driver", "mechanic", "strategist"]
    if role not in valid_roles:
        return f"Error: role must be one of {valid_roles}."
    data.crew_members[name] = {"role": role, "skill_level": 1}
    return f"Registered {name} as {role}."

def view_members():
    """to view all registered members and their roles"""
    if not data.crew_members:
        return "No crew members registered."
    for name, info in data.crew_members.items():
        print(f"  {name} | Role: {info['role']} | Skill: {info['skill_level']}")