
# Code for the Personal Activity Tracker, PATapp.

def save_details(file, details):
    print("testi")

def set_physique():
    weight = input("Enter your weight in kg without decimals: ")
    save_details("physique", weight)
    print("Physique saved!")

def get_physique():
    return "50"

def calculate_calories(weight, distance):
    # Calories burned ≈ body mass (kg) × distance (km) × 1 kcal·kg⁻¹·km⁻¹
    print(f"Calculating calories..."
          f"\t{weight} kg * {distance} km * 1 kcal*kg^(-1)*km^(-1) = {weight * distance}"
          f"\tDone!")
    return (weight * distance)

def session_details_input():
    date = input("Date exercised (in format dd.mm.yy): ")
    time = input("Time exercised (in format hh:mm:ss): ")
    distance = input("Distance travelled in meters: ")
    print(f"Date: {date}\nTime: {time}\nDistance: {distance}")
    save_details("sessions", f"{date}-{time}-{distance}-{calculate_calories(get_physique(), distance)}")
    print(f"Details saved!")

if __name__ == '__main__':
    session_details_input()
