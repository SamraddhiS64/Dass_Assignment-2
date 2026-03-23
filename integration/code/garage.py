import data
import inventory
import crew
import inventory

def repair_car(car_name, mechanic_name):
    # must be a registered mechanic
    if mechanic_name not in data.crew_members:
        return f"Error: '{mechanic_name}' not registered."
    if data.crew_members[mechanic_name]["role"] != "mechanic":
        return f"Error: '{mechanic_name}' is not a mechanic."
    for car in data.inventory["cars"]:
        if car["name"] == car_name:
            if not car["damaged"]:
                return f"'{car_name}' is not damaged."
            result = inventory.deduct_parts(2)   # repair costs 2 parts (general rule)
            if result.startswith("Error"):
                return result
            car["damaged"] = False
            return f"'{car_name}' repaired by {mechanic_name}."
    return f"Car '{car_name}' not found."

def view_car_status():
    for car in data.inventory["cars"]:
        status = "DAMAGED" if car["damaged"] else "Ready"
        print(f"  {car['name']} — {status}")