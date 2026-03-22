import data

def add_car(car_name):
    data.inventory["cars"].append({"name": car_name, "damaged": False})
    return f"Car '{car_name}' added to inventory."

def add_parts(quantity):
    data.inventory["spare_parts"] += quantity
    return f"Added {quantity} spare parts."

def deduct_parts(quantity):
    if quantity <= 0:
        return "Error: quantity must be greater than 0."
    if data.inventory["spare_parts"] < quantity:
        return f"Error: not enough spare parts. Available: {data.inventory['spare_parts']}."
    data.inventory["spare_parts"] -= quantity
    return f"Deducted {quantity} spare parts. Remaining: {data.inventory['spare_parts']}."

def add_tools(quantity):
    data.inventory["tools"] += quantity
    return f"Added {quantity} tools."

def update_cash(amount):
    data.inventory["cash"] += amount
    status = "added" if amount >= 0 else "deducted"
    return f"${abs(amount)} {status}. Balance: ${data.inventory['cash']}"

def view_inventory():
    inv = data.inventory
    print(f"  Cash: ${inv['cash']}")
    print(f"  Cars: {[c['name'] for c in inv['cars']]}")
    print(f"  Spare parts: {inv['spare_parts']}")
    print(f"  Tools: {inv['tools']}")

def get_available_cars():
    return [c for c in data.inventory["cars"] if not c["damaged"]]

def mark_car_damaged(car_name):
    for car in data.inventory["cars"]:
        if car["name"] == car_name:
            car["damaged"] = True
            return f"'{car_name}' marked as damaged."
    return "Car not found."