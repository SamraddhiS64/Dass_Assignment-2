import data
import inventory
from race import _find_race

def record_result(race_name, winner_name, car_damaged=False):
    race = _find_race(race_name)
    if not race:
        return f"Error: race '{race_name}' not found."
    if race["completed"]:
        return f"Error: race '{race_name}' already completed."
    if winner_name not in race["drivers"]:
        return f"Error: '{winner_name}' was not entered in this race."

    race["completed"] = True
    result = {"race": race_name, "winner": winner_name, "prize": race["prize"], "car_damaged": car_damaged}
    data.results.append(result)

    # Update cash balance (business rule: prize money flows to inventory)
    inventory.update_cash(race["prize"])

    if car_damaged and race["car"]:
        inventory.mark_car_damaged(race["car"])

    return f"Result recorded: {winner_name} won '{race_name}' and earned ${race['prize']}."

def view_rankings():
    tally = {}
    for r in data.results:
        w = r["winner"]
        tally[w] = tally.get(w, {"wins": 0, "earnings": 0})
        tally[w]["wins"] += 1
        tally[w]["earnings"] += r["prize"]
    print("  Rankings:")
    for name, stats in sorted(tally.items(), key=lambda x: -x[1]["wins"]):
        print(f"    {name} | Wins: {stats['wins']} | Earnings: ${stats['earnings']}")

