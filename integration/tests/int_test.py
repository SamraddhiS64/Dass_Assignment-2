import sys
import os
"""
Tests are grouped by how many modules interact:
  - 2-module tests
  - 3-module tests
  - 4-module tests
  - 5-module tests
Each test resets data_store before running.
"""

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

import data
import registration
import crew
import inventory
import race
import results
import mission
import garage
import leaderboard


# HELPER: reset all shared state before each test
def reset():
    data.crew_members.clear()
    data.inventory["cars"] = []
    data.inventory["spare_parts"] = 0
    data.inventory["tools"] = 0
    data.inventory["cash"] = 1000
    data.races.clear()
    data.results.clear()
    data.missions.clear()


def run_test(name, result, expected):
    status = "PASS" if result == expected else "FAIL"
    print(f"  [{status}] {name}")
    if status == "FAIL":
        print(f"         Expected : {expected}")
        print(f"         Got      : {result}")


# 2-MODULE TESTS

def test_registration_crew_assign_role_requires_registration():
    """crew depends on registration: assign_role must fail for unknown member."""
    reset()
    result = crew.assign_role("Ghost", "driver")
    run_test(
        "assign_role fails if member not registered (registration → crew)",
        result,
        "Error: 'Ghost' not registered. Register first."
    )


def test_registration_crew_assign_role_success():
    """Register then change role — crew reads registration data."""
    reset()
    registration.register("Letty", "driver")
    result = crew.assign_role("Letty", "mechanic")
    run_test(
        "assign_role succeeds after registration (registration → crew)",
        result,
        "Letty's role updated to mechanic."
    )


def test_inventory_add_and_view_cash():
    """update_cash adds to the balance stored in data_store (inventory → data_store)."""
    reset()
    inventory.update_cash(500)
    run_test(
        "Cash balance increases after update_cash (inventory → data_store)",
        data.inventory["cash"],
        1500
    )


def test_inventory_deduct_parts_insufficient():
    """deduct_parts blocks when stock is 0 (inventory internal guard)."""
    reset()
    result = inventory.deduct_parts(3)
    run_test(
        "deduct_parts fails with no stock (inventory → data_store)",
        result,
        "Error: not enough spare parts. Available: 0."
    )


def test_inventory_add_then_deduct_parts():
    """Add parts then deduct — balance must be correct."""
    reset()
    inventory.add_parts(10)
    inventory.deduct_parts(4)
    run_test(
        "Spare parts balance correct after add then deduct (inventory → data_store)",
        data.inventory["spare_parts"],
        6
    )

def test_view_car_status_reflects_damage_and_repair():
    """
    Add a car → damage it → repair it → view_car_status must show
    the car as ready (not damaged).
    Modules: registration → inventory → garage → garage.view_car_status → inventory
    """
    reset()
    registration.register("Letty", "mechanic")
    inventory.add_car("Supra")
    inventory.add_parts(5)
    inventory.mark_car_damaged("Supra")
    garage.repair_car("Supra", "Letty")
    # view_car_status reads inventory cars — check the flag directly
    # since view_car_status prints, we verify the underlying state it reads
    car = next((c for c in data.inventory["cars"] if c["name"] == "Supra"), None)
    run_test(
        "view_car_status reflects repaired car as not damaged (garage → inventory)",
        car["damaged"] if car else None,
        False
    )


# 3-MODULE TESTS

def test_registration_crew_race_non_driver_blocked():
    """Register as mechanic → enter race → must be blocked (registration → crew → race)."""
    reset()
    registration.register("Tej", "mechanic")
    inventory.add_car("Skyline")
    race.create_race("Quarter Mile", 2000)
    result = race.enter_driver("Quarter Mile", "Tej", "Skyline")
    run_test(
        "Mechanic cannot enter race (registration → crew → race)",
        result,
        "Error: 'Tej' is not a driver."
    )


def test_registration_crew_race_driver_success():
    """Register as driver → enter race → must succeed."""
    reset()
    registration.register("Dom", "driver")
    inventory.add_car("Charger")
    race.create_race("Toretto Cup", 5000)
    result = race.enter_driver("Toretto Cup", "Dom", "Charger")
    run_test(
        "Driver enters race successfully (registration → inventory → race)",
        result,
        "Dom entered 'Toretto Cup' driving Charger."
    )


def test_race_results_cash_updates():
    """Complete a race → prize must be added to inventory cash (race → results → inventory)."""
    reset()
    registration.register("Brian", "driver")
    inventory.add_car("Supra")
    race.create_race("Tokyo Drift", 3000)
    race.enter_driver("Tokyo Drift", "Brian", "Supra")
    results.record_result("Tokyo Drift", "Brian")
    run_test(
        "Prize added to cash after race (race → results → inventory)",
        data.inventory["cash"],
        4000   # 1000 starting + 3000 prize
    )


def test_registration_crew_mission_missing_role():
    """Register only a driver — mission needing mechanic must fail (registration → crew → mission)."""
    reset()
    registration.register("Roman", "driver")
    result = mission.assign_mission("Nitro Heist", "heist", ["mechanic"])
    run_test(
        "Mission blocked when required role absent (registration → crew → mission)",
        result,
        "Error: mission cannot start. Missing roles: ['mechanic']."
    )


def test_registration_crew_mission_all_roles_present():
    """Register driver + mechanic — mission needing both must succeed."""
    reset()
    registration.register("Roman", "driver")
    registration.register("Tej", "mechanic")
    result = mission.assign_mission("Nitro Heist", "heist", ["driver", "mechanic"])
    run_test(
        "Mission succeeds when all roles present (registration → crew → mission)",
        result,
        "Mission 'Nitro Heist' (heist) assigned. Roles confirmed: ['driver', 'mechanic']."
    )

def test_update_skill_stored_and_readable():
    """
    Register a member → update their skill level → confirm it is
    stored correctly in data.crew_members.
    Modules: registration → crew → data
    """
    reset()
    registration.register("Dom", "driver")
    crew.update_skill("Dom", 8)
    run_test(
        "Skill level stored correctly after update_skill (registration → crew → data)",
        data.crew_members["Dom"]["skill_level"],
        8
    )

def test_leaderboard_includes_zero_win_crew_members():
    """
    Register a crew member but run no races → they must still appear
    on the leaderboard with 0 wins, because get_leaderboard loops
    over data.crew_members as well as data.results.
    Modules: registration → leaderboard → data
    """
    reset()
    registration.register("Roman", "driver")
    registration.register("Dom", "driver")
    inventory.add_car("Charger")
    race.create_race("One Race", 2000)
    race.enter_driver("One Race", "Dom", "Charger")
    results.record_result("One Race", "Dom")
    board = leaderboard.get_leaderboard()
    names_on_board = [entry[0] for entry in board]
    run_test(
        "Zero-win crew member appears on leaderboard (registration → leaderboard → data)",
        "Roman" in names_on_board,
        True
    )


# 4-MODULE TESTS

def test_race_results_inventory_car_marked_damaged():
    """
    Race with damage flag → car must appear damaged in inventory.
    Modules: registration → race → results → inventory
    """
    reset()
    registration.register("Han", "driver")
    inventory.add_car("RX-7")
    race.create_race("Drift Battle", 4000)
    race.enter_driver("Drift Battle", "Han", "RX-7")
    results.record_result("Drift Battle", "Han", car_damaged=True)
    damaged_cars = [c for c in data.inventory["cars"] if c["damaged"]]
    run_test(
        "Car flagged damaged after race (registration → race → results → inventory)",
        damaged_cars[0]["name"] if damaged_cars else None,
        "RX-7"
    )


def test_damaged_car_blocked_from_next_race():
    """
    Damage a car in race 1 → try to enter race 2 → must be blocked.
    Modules: registration → race → results → inventory → race
    """
    reset()
    registration.register("Han", "driver")
    inventory.add_car("RX-7")
    race.create_race("Race 1", 2000)
    race.enter_driver("Race 1", "Han", "RX-7")
    results.record_result("Race 1", "Han", car_damaged=True)
    race.create_race("Race 2", 2000)
    result = race.enter_driver("Race 2", "Han", "RX-7")
    run_test(
        "Damaged car blocked from entering next race (race → results → inventory → race)",
        result,
        "Error: car 'RX-7' is not available (damaged or missing)."
    )


def test_garage_repair_restores_car():
    """
    Damage a car → add parts → repair → car available again.
    Modules: registration → inventory → garage → inventory
    """
    reset()
    registration.register("Letty", "mechanic")
    inventory.add_car("Mustang")
    inventory.add_parts(5)
    inventory.mark_car_damaged("Mustang")
    garage.repair_car("Mustang", "Letty")
    available = [c["name"] for c in inventory.get_available_cars()]
    run_test(
        "Repaired car is available again (registration → inventory → garage → inventory)",
        "Mustang" in available,
        True
    )


def test_garage_repair_deducts_parts():
    """
    Repair must consume 2 spare parts from inventory.
    Modules: registration → inventory → garage → inventory
    """
    reset()
    registration.register("Letty", "mechanic")
    inventory.add_car("Mustang")
    inventory.add_parts(5)
    inventory.mark_car_damaged("Mustang")
    garage.repair_car("Mustang", "Letty")
    run_test(
        "Spare parts deducted after repair (registration → inventory → garage → inventory)",
        data.inventory["spare_parts"],
        3   # 5 added - 2 used
    )


def test_garage_repair_fails_no_parts():
    """
    No spare parts → repair must fail and car stays damaged.
    Modules: registration → inventory → garage → inventory
    """
    reset()
    registration.register("Letty", "mechanic")
    inventory.add_car("Mustang")
    inventory.mark_car_damaged("Mustang")
    result = garage.repair_car("Mustang", "Letty")
    still_damaged = any(c["damaged"] for c in data.inventory["cars"] if c["name"] == "Mustang")
    run_test(
        "Repair blocked with no parts, car stays damaged (registration → inventory → garage → inventory)",
        (result.startswith("Error") and still_damaged),
        True
    )


# 5-MODULE TESTS

def test_full_race_then_repair_then_reenter():
    """
    Full cycle: register driver + mechanic → race → damage car →
    add parts → repair → enter next race.
    Modules: registration → race → results → inventory → garage → race
    """
    reset()
    registration.register("Dom", "driver")
    registration.register("Letty", "mechanic")
    inventory.add_car("Charger")
    inventory.add_parts(5)
    race.create_race("Race 1", 3000)
    race.enter_driver("Race 1", "Dom", "Charger")
    results.record_result("Race 1", "Dom", car_damaged=True)
    garage.repair_car("Charger", "Letty")
    race.create_race("Race 2", 3000)
    result = race.enter_driver("Race 2", "Dom", "Charger")
    run_test(
        "Repaired car re-enters race (registration → race → results → inventory → garage → race)",
        result,
        "Dom entered 'Race 2' driving Charger."
    )


def test_results_flow_into_leaderboard():
    """
    Run two races → leaderboard must rank by wins correctly.
    Modules: registration → race → results → inventory → leaderboard
    """
    reset()
    registration.register("Dom", "driver")
    registration.register("Brian", "driver")
    inventory.add_car("Charger")
    inventory.add_car("Supra")
    race.create_race("Race A", 2000)
    race.enter_driver("Race A", "Dom", "Charger")
    results.record_result("Race A", "Dom")
    race.create_race("Race B", 2000)
    race.enter_driver("Race B", "Dom", "Supra")
    results.record_result("Race B", "Dom")
    race.create_race("Race C", 2000)
    race.enter_driver("Race C", "Brian", "Charger")
    results.record_result("Race C", "Brian")
    board = leaderboard.get_leaderboard()
    run_test(
        "Dom ranked first with 2 wins (registration → race → results → inventory → leaderboard)",
        board[0][0],
        "Dom"
    )
    run_test(
        "Brian ranked second with 1 win (registration → race → results → inventory → leaderboard)",
        board[1][0],
        "Brian"
    )


def test_mission_after_race_damages_only_mechanic():
    """
    Race damages car → mechanic still available → mission needing mechanic must pass.
    Modules: registration → race → results → inventory → mission → crew
    """
    reset()
    registration.register("Dom", "driver")
    registration.register("Letty", "mechanic")
    inventory.add_car("Charger")
    inventory.add_parts(5)
    race.create_race("Canyon Run", 4000)
    race.enter_driver("Canyon Run", "Dom", "Charger")
    results.record_result("Canyon Run", "Dom", car_damaged=True)
    result = mission.assign_mission("Parts Run", "supply", ["mechanic"])
    run_test(
        "Mission finds mechanic even after car is damaged (registration → race → results → inventory → mission → crew)",
        result,
        "Mission 'Parts Run' (supply) assigned. Roles confirmed: ['mechanic']."
    )


def test_cash_accumulates_across_multiple_races():
    """
    Win 3 races → cash must equal 1000 + sum of all prizes.
    Modules: registration → inventory → race → results → inventory
    """
    reset()
    registration.register("Dom", "driver")
    inventory.add_car("Charger")
    prizes = [2000, 3500, 5000]
    for i, prize in enumerate(prizes):
        rname = f"Race {i+1}"
        race.create_race(rname, prize)
        race.enter_driver(rname, "Dom", "Charger")
        results.record_result(rname, "Dom")
    run_test(
        "Cash accumulates correctly across 3 races (registration → inventory → race → results → inventory)",
        data.inventory["cash"],
        1000 + sum(prizes)   # 11500
    )


# RUN ALL TESTS

if __name__ == "__main__":
    # 2-module
    test_registration_crew_assign_role_requires_registration()
    test_registration_crew_assign_role_success()
    test_inventory_add_and_view_cash()
    test_inventory_deduct_parts_insufficient()
    test_inventory_add_then_deduct_parts()
    test_view_car_status_reflects_damage_and_repair()

    # 3-module
    test_registration_crew_race_non_driver_blocked()
    test_registration_crew_race_driver_success()
    test_race_results_cash_updates()
    test_registration_crew_mission_missing_role()
    test_registration_crew_mission_all_roles_present()
    test_update_skill_stored_and_readable()
    test_leaderboard_includes_zero_win_crew_members()

    # 4-module
    test_race_results_inventory_car_marked_damaged()
    test_damaged_car_blocked_from_next_race()
    test_garage_repair_restores_car()
    test_garage_repair_deducts_parts()
    test_garage_repair_fails_no_parts()

    # 5-module
    test_full_race_then_repair_then_reenter()
    test_results_flow_into_leaderboard()
    test_mission_after_race_damages_only_mechanic()
    test_cash_accumulates_across_multiple_races()

    print("\nDone.")