import data
import crew
import inventory

def create_race(race_name, prize_money):
    race = {"name": race_name, "prize": prize_money, "drivers": [], "car": None, "completed": False}
    data.races.append(race)
    return f"Race '{race_name}' created with ${prize_money} prize."

def enter_driver(race_name, driver_name, car_name):
    race = _find_race(race_name)
    if not race:
        return f"Error: race '{race_name}' not found."
    # must be a registered driver
    if driver_name not in data.crew_members:
        return f"Error: '{driver_name}' is not registered."
    if data.crew_members[driver_name]["role"] != "driver":
        return f"Error: '{driver_name}' is not a driver."
    # must use an undamaged car
    available = [c["name"] for c in inventory.get_available_cars()]
    if car_name not in available:
        return f"Error: car '{car_name}' is not available (damaged or missing)."
    race["drivers"].append(driver_name)
    race["car"] = car_name
    return f"{driver_name} entered '{race_name}' driving {car_name}."

def view_races():
    for r in data.races:
        status = "Completed" if r["completed"] else "Open"
        print(f"  {r['name']} | Prize: ${r['prize']} | Status: {status} | Drivers: {r['drivers']}")

def _find_race(name):
    for r in data.races:
        if r["name"] == name:
            return r
    return None