import data
import crew

def assign_mission(mission_name, mission_type, required_roles):
    # Check all required roles are present in the crew
    missing = []
    for role in required_roles:
        available = crew.get_members_by_role(role)
        if not available:
            missing.append(role)
    if missing:
        return f"Error: mission cannot start. Missing roles: {missing}."
    mission = {"name": mission_name, "type": mission_type, "required_roles": required_roles, "status": "active"}
    data.missions.append(mission)
    return f"Mission '{mission_name}' ({mission_type}) assigned. Roles confirmed: {required_roles}."

def view_missions():
    for m in data.missions:
        print(f"  {m['name']} | Type: {m['type']} | Status: {m['status']} | Roles: {m['required_roles']}")