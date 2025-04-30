
# Code for the Personal Activity Tracker, PATapp.

def save_to_file(file, mode, details):
    print(f"Destination: {file}\nDetails: {details}")
    with open(file, mode) as f:
        f.write(details)
    print(f"Saved!")

def get_file_content(file):
    print(f"Source: {file}")
    with open(file) as f:
        content = f.read()
        print(f"Content: {content}")
        return content

def set_physique():
    while True:
        weight = input("Enter your weight in kg without decimals: ")
        try:
            if int(weight) < 0 or int(weight) > 1000:
                raise ValueError
            break
        except ValueError:
            print(f"Invalid input.")
    save_to_file("physique.txt", "w", weight)

def calculate_calories(weight, distance):
    # Calories burned ≈ body mass (kg) × distance (km) × 1 kcal·kg⁻¹·km⁻¹
    calories = int(weight) * int(distance)
    print(f"Calculating calories..."
          f"\t{weight} kg * {distance} km * 1 kcal*kg^(-1)*km^(-1) = {calories}"
          f"\tDone!")
    return calories

def check_input(input, mode):
    if mode == "d":
        try:
            if int(input) < 0:
                raise ValueError
            return True
        except ValueError:
            print(f"Invalid input.")
            return False
    characters = list(input)
    try:
        if characters[2] != mode or characters[5] != mode:
            raise IndexError
        parts = input.split(mode)
        if mode == ".":
            first = 32
            second = 12
            third = 99
            lowest = 1
        else:
            first = 99
            second = 59
            third = 59
            lowest = 0
        if int(parts[0]) < lowest or int(parts[0]) > first or int(parts[1]) < lowest or int(parts[1]) > second or int(parts[2]) < lowest or int(parts[2]) > third:
            raise ValueError
    except (IndexError, ValueError):
        print(f"Invalid input.")
        return False
    return True

def session_details_input():
    while True:
        date = input("Date exercised (in format dd.mm.yy): ")
        if check_input(date, "."):
            break
    while True:
        time = input("Time exercised (in format hh:mm:ss): ")
        if check_input(time, ":"):
            break
    while True:
        distance = input("Distance travelled in meters without decimals: ")
        if check_input(distance, "d"):
            break
    save_to_file("sessions.txt", "a", f"{date}-{time}-{distance}-{calculate_calories(get_file_content("physique.txt"), distance)}\n")

def cli_menu():
    while True:
        heti = input("Add new session details? (y/n): ")
        if check_input(heti, "heti"):
            if heti.strip().lower() == "y":
                session_details_input()
            else:
                break
    while True:
        print(f"\nWelcome to PATapp!"
              f"\n"
              f"\n[1] Draw graphs"
              f"\n[2] Add new session details"
              f"\n[3] Replace existing physique ({get_file_content("physique.txt")} kg)"
              f"\n")

if __name__ == '__main__':
    try:
        open("physique.txt", "x")
        set_physique()
    except FileExistsError:
        pass
    session_details_input()
