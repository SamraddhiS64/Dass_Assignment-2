import registration, crew, inventory, race, results, mission, leaderboard, garage

def main():
    while True:
        print("\n=== StreetRace Manager ===")
        print("1. Registration  2. Crew  3. Inventory")
        print("4. Race          5. Results  6. Missions")
        print("7. Leaderboard   8. Garage   9. Quit")
        choice = input("Choose: ").strip()

        if choice == "1":
            name = input("Name: ")
            role = input("Role (driver/mechanic/strategist): ")
            print(registration.register_member(name, role))

        elif choice == "2":
            print("1. Assign role  2. Update skill  3. View members")
            c = input(">> ")
            if c == "1":
                name = input("Name: "); role = input("New role: ")
                print(crew.assign_role(name, role))
            elif c == "2":
                name = input("Name: "); lvl = int(input("Skill level (1-10): "))
                print(crew.update_skill(name, lvl))
            elif c == "3":
                registration.view_members()

        elif choice == "3":
            print("1. Add car  2. Add parts  3. Add cash  4. View")
            c = input(">> ")
            if c == "1": print(inventory.add_car(input("Car name: ")))
            elif c == "2": print(inventory.add_parts(int(input("Quantity: "))))
            elif c == "3": print(inventory.update_cash(int(input("Amount: "))))
            elif c == "4": inventory.view_inventory()

        elif choice == "4":
            print("1. Create race  2. Enter driver  3. View races")
            c = input(">> ")
            if c == "1":
                name = input("Race name: "); prize = int(input("Prize: "))
                print(race.create_race(name, prize))
            elif c == "2":
                r = input("Race: "); d = input("Driver: "); car = input("Car: ")
                print(race.enter_driver(r, d, car))
            elif c == "3": race.view_races()

        elif choice == "5":
            print("1. Record result  2. View rankings")
            c = input(">> ")
            if c == "1":
                r = input("Race: "); w = input("Winner: ")
                dmg = input("Car damaged? (y/n): ").lower() == "y"
                print(results.record_result(r, w, dmg))
            elif c == "2": results.view_rankings()

        elif choice == "6":
            print("1. Assign mission  2. View missions")
            c = input(">> ")
            if c == "1":
                n = input("Mission name: "); t = input("Type: ")
                roles = input("Required roles (comma-separated): ").split(",")
                roles = [r.strip() for r in roles]
                print(mission.assign_mission(n, t, roles))
            elif c == "2": mission.view_missions()

        elif choice == "7":
            leaderboard.print_leaderboard()

        elif choice == "8":
            print("1. Repair car  2. View car status")
            c = input(">> ")
            if c == "1":
                car = input("Car name: "); mech = input("Mechanic name: ")
                print(garage.repair_car(car, mech))
            elif c == "2": garage.view_car_status()

        elif choice == "9":
            print("Exiting."); break

if __name__ == "__main__":
    main()