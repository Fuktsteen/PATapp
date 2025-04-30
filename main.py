# Code for the Personal Activity Tracker, PATapp.

import time

from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QStackedWidget, QLineEdit, \
    QHBoxLayout, QLabel


def save_to_file(file, mode, details):
    #print(f"Destination: {file}\nDetails: {details}")
    with open(file, mode) as f:
        f.write(details)
    print(f"Saved!")

def get_file_content(file):
    #print(f"Source: {file}")
    with open(file) as f:
        content = f.read()
        #print(f"Content: {content}")
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
    if input.strip() == "":
        print(f"Invalid input.")
        return False
    elif mode == "d":
        try:
            if int(input) < 0:
                raise ValueError
            return True
        except ValueError:
            print(f"Invalid input.")
            return False
    elif mode == "heti":
        try:
            if input.strip().lower() == "y" or input.strip().lower() == "n":
                return True
            else:
                raise AttributeError
        except AttributeError:
            print(f"Invalid input.")
            return False
    elif mode == "menu":
        try:
            if int(input.strip()) in [1, 2, 3, 4, 5]:
                return True
            else:
                raise ValueError
        except (ValueError, AttributeError):
            print(f"Invalid input.")
            return False
    else:
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

def fetch_session_details():
    raw_sessions = get_file_content("sessions.txt")
    fine_sessions = []
    session_data = raw_sessions.split("\n")
    for raw_session in session_data:
        fine_sessions.append(raw_session.split("-"))
    fine_sessions.pop()
    #print(fine_sessions)
    return fine_sessions

def edit_session_details():
    pass

def cli_menu():
    try:
        open("physique.txt", "x")
        set_physique()
    except FileExistsError:
        pass
    while True:
        heti = input("Add new session details? (y/n): ")
        if check_input(heti, "heti"):
            if heti.strip().lower() == "y":
                session_details_input()
                break
            else:
                break
    running = True
    while running:
        all_sessions = fetch_session_details()
        print("debug", all_sessions)
        print(f"\nWelcome to PATapp!"
              f"\n"
              f"\n[1] Draw graphs"
              f"\n[2] Add new session details"
              f"\n[3] Edit session details ({len(all_sessions)} saved sessions)"
              f"\n[4] Replace existing physique ({get_file_content("physique.txt")} kg)"
              f"\n[5] Exit"
              f"\n")
        while True:
            menuInput = input("What would you like to do? (give only a number): ")
            if check_input(menuInput, "menu"):
                if int(menuInput.strip()) == 1:
                    print(f"WIP")
                    break
                elif int(menuInput.strip()) == 2:
                    session_details_input()
                    break
                elif int(menuInput.strip()) == 3:
                    print(f"WIP")
                    break
                elif int(menuInput.strip()) == 4:
                    set_physique()
                    break
                elif int(menuInput.strip()) == 5:
                    running = False
                    break
    print(f"Thank you for using PATapp. Exiting...")
    time.sleep(1)

class Menu(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.draw_graphs = QPushButton("Draw graphs")
        self.new_session = QPushButton("Add new session details")
        self.edit_session = QPushButton("Edit session details")
        self.replace_physique = QPushButton("Replace existing physique")
        self.exit_button = QPushButton("Exit")

        self.draw_graphs.clicked.connect(lambda: self.switch_view.emit(1))
        self.new_session.clicked.connect(lambda: self.switch_view.emit(1))
        self.edit_session.clicked.connect(lambda: self.switch_view.emit(1))
        self.replace_physique.clicked.connect(lambda: self.switch_view.emit(1))
        self.exit_button.clicked.connect(lambda: exit())
        layout.addWidget(self.draw_graphs)
        layout.addWidget(self.new_session)
        layout.addWidget(self.edit_session)
        layout.addWidget(self.replace_physique)
        layout.addWidget(self.exit_button)

class AddSession(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # need date, time and distance layers
        dateLayer = QHBoxLayout()
        self.dateLabel = QLabel("Date exercised (in format dd.mm.yy): ")
        self.dateInput = QLineEdit()
        self.dateInput.textChanged.connect(lambda: self.input_checker(self.dateInput.text(), ":"))
        dateLayer.addWidget(self.dateLabel)
        dateLayer.addWidget(self.dateInput)

        timeLayer = QHBoxLayout()
        self.timeLabel = QLabel("Time exercised (in hh:mm:ss): ")
        self.timeInput = QLineEdit()
        self.timeInput.textChanged.connect(lambda: self.input_checker(self.timeInput.text(), "."))
        timeLayer.addWidget(self.timeLabel)
        timeLayer.addWidget(self.timeInput)

        matkaLayer = QHBoxLayout()
        self.matkaLabel = QLabel("Distance travelled in meters without decimals: ")
        self.matkaInput = QLineEdit()
        self.matkaInput.textChanged.connect(lambda: self.input_checker(self.matkaInput.text(), "d"))
        matkaLayer.addWidget(self.matkaLabel)
        matkaLayer.addWidget(self.matkaInput)

        self.submitButton = QPushButton("Save")
        self.submitButton.clicked.connect(lambda: self.save_handler(self.dateInput.text(), self.timeInput.text(), self.matkaInput.text()))

        layout.addLayout(dateLayer)
        layout.addLayout(timeLayer)
        layout.addLayout(matkaLayer)
        layout.addWidget(self.submitButton)

    def save_handler(self, date, time, distance):
        print(f"debug {date} {time} {distance}")
        self.switch_view.emit(0)

    def input_checker(self, candidate, mode):
        print(f"debug {candidate} {mode}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Activity Tracker - PATapp")
        self.setMinimumSize(QSize(400, 300))
        self.setMaximumSize(QSize(1200, 900))

        self.stack = QStackedWidget()
        self.menuview = Menu()
        self.menuview.switch_view.connect(self.stack.setCurrentIndex)
        self.newseshview = AddSession()
        self.newseshview.switch_view.connect(self.stack.setCurrentIndex)
        self.stack.addWidget(self.menuview)
        self.stack.addWidget(self.newseshview)

        self.stack.setCurrentIndex(0)

        self.setCentralWidget(self.stack)

if __name__ == '__main__':
    app = QApplication([])

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()
    #cli_menu()
