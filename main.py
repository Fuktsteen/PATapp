# Code for the Personal Activity Tracker, PATapp.

import time

from PyQt5.QtCore import QSize, pyqtSignal, Qt
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
    calories = int(weight) * (int(distance) / 1000)
    print(f"Calculating calories..."
          f"\t{weight} kg * {int(distance) / 1000} km * 1 kcal*kg^(-1)*km^(-1) = {calories}"
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
    elif mode == "physique":
        try:
            if int(input.strip()) < 0:
                raise ValueError
        except ValueError:
            print(f"Invalid input.")
            return False
    else:
        characters = list(input)
        try:
            if characters[2] != mode or characters[5] != mode:
                raise IndexError
            parts = input.split(mode)
            if mode == ".":
                first = 31
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
        layout.setAlignment(Qt.AlignTop)
        self.draw_graphs = QPushButton("Draw graphs")
        self.new_session = QPushButton("Add new session details")
        self.edit_session = QPushButton()
        self.replace_physique = QPushButton()
        self.exit_button = QPushButton("Exit")

        self.draw_graphs.clicked.connect(lambda: self.switch_view.emit(4))
        self.new_session.clicked.connect(lambda: self.switch_view.emit(1))
        self.edit_session.clicked.connect(lambda: self.switch_view.emit(3))
        self.replace_physique.clicked.connect(lambda: self.switch_view.emit(2))
        self.exit_button.clicked.connect(lambda: exit())
        layout.addWidget(self.draw_graphs)
        layout.addWidget(self.new_session)
        layout.addWidget(self.edit_session)
        layout.addWidget(self.replace_physique)
        layout.addWidget(self.exit_button)

    def showEvent(self, event):
        self.edit_session.setText(f"Show session details ({len(fetch_session_details())} saved sessions)")
        self.replace_physique.setText(f"Replace existing physique ({get_file_content("physique.txt")} kg)")
        super().showEvent(event)

class DrawGraphs(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        buttonLayer = QHBoxLayout()
        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(lambda: self.switch_view.emit(0))
        buttonLayer.addWidget(self.backButton)

        layout.addLayout(buttonLayer)

class ShowSessions(QWidget):
    switch_view = pyqtSignal(int)
    tarkastaja = 0
    session_data = []
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        buttonLayer = QHBoxLayout()
        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(lambda: self.switch_view.emit(0))
        self.deleteButton = QPushButton("Delete")
        self.deleteButton.setDisabled(True)
        self.deleteButton.clicked.connect(lambda: self.delete_handler(self.chooseInput.text()))
        buttonLayer.addWidget(self.backButton)
        buttonLayer.addWidget(self.deleteButton)

        inputLayer = QHBoxLayout()
        self.chooseLabel = QLabel(f"Choose session to delete (number):")
        self.chooseInput = QLineEdit()
        self.chooseInput.textChanged.connect(lambda: self.input_checker(self.chooseInput.text()))
        inputLayer.addWidget(self.chooseLabel)
        inputLayer.addWidget(self.chooseInput)

        self.sessionDetail = QLabel()
        layout.addLayout(buttonLayer)
        layout.addLayout(inputLayer)
        layout.addWidget(self.sessionDetail)

    def input_checker(self, candidate):
        try:
            if int(candidate) < 1 or int(candidate) > self.tarkastaja:
                raise ValueError
            self.deleteButton.setEnabled(True)
        except ValueError:
            self.deleteButton.setDisabled(True)

    def delete_handler(self, choice):
        print("VANHA")
        for id, i in enumerate(self.session_data):
            print(id, i)
        print("\nUUS")
        self.session_data.pop(int(choice)-1)
        for id, i in enumerate(self.session_data):
            print(id, i)

    def showEvent(self, event):
        self.session_data = fetch_session_details()
        self.tarkastaja = len(self.session_data)
        session_text = ""
        for id, session in enumerate(self.session_data):
            session_text += f"{id+1}.       Date: {session[0]}      Duration: {session[1]}      Distance: {session[2]}      Burned calories: {session[3]}\n"
        if session_text == "":
            self.sessionDetail.setAlignment(Qt.AlignCenter)
            session_text = f"No saved sessions."
        else:
            self.sessionDetail.setAlignment(Qt.AlignLeft)
        self.sessionDetail.setText(session_text)
        self.chooseInput.setText("")
        super().showEvent(event)
        
class Physique(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # need layers for info, input and buttons
        infoLayer = QHBoxLayout()
        self.infoLabel = QLabel()
        infoLayer.addWidget(self.infoLabel)

        inputLayer = QHBoxLayout()
        self.physiqueLabel = QLabel("Enter your weight in kg without decimals:")
        self.physiqueInput = QLineEdit()
        self.physiqueInput.textChanged.connect(lambda: self.input_checker(self.physiqueInput.text()))
        inputLayer.addWidget(self.physiqueLabel)
        inputLayer.addWidget(self.physiqueInput)

        buttonLayer = QHBoxLayout()
        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(lambda: self.switch_view.emit(0))
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(lambda: self.save_handler(self.physiqueInput.text()))
        self.saveButton.setDisabled(True)
        buttonLayer.addWidget(self.backButton)
        buttonLayer.addWidget(self.saveButton)

        layout.addLayout(infoLayer)
        layout.addLayout(inputLayer)
        layout.addLayout(buttonLayer)

    def showEvent(self, event):
        self.infoLabel.setText(f"Your current saved physique is {get_file_content('physique.txt')} kg."
                                f"\nThis is used to estimate burned calories based on distance exercised:"
                                f"\nCalories burned ≈ body mass (kg) × distance (km) × 1 kcal·kg⁻¹·km⁻¹")
        super().showEvent(event)

    def save_handler(self, weight):
        save_to_file("physique.txt", "w", weight)
        self.physiqueInput.setText("")
        self.switch_view.emit(0)

    def input_checker(self, candidate):
        if check_input(candidate, "physique"):
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setEnabled(False)

class AddSession(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # need date, time and distance layers
        self.inputChecker = [ [".", False], [":", False], ["d", False] ]

        dateLayer = QHBoxLayout()
        self.dateLabel = QLabel("Date exercised (dd.mm.yy):")
        self.dateInput = QLineEdit()
        self.dateInput.textChanged.connect(lambda: self.input_checker(self.dateInput.text(), "."))
        dateLayer.addWidget(self.dateLabel)
        dateLayer.addWidget(self.dateInput)

        timeLayer = QHBoxLayout()
        self.timeLabel = QLabel("Time exercised (hh:mm:ss):")
        self.timeInput = QLineEdit()
        self.timeInput.textChanged.connect(lambda: self.input_checker(self.timeInput.text(), ":"))
        timeLayer.addWidget(self.timeLabel)
        timeLayer.addWidget(self.timeInput)

        matkaLayer = QHBoxLayout()
        self.matkaLabel = QLabel("Distance travelled in meters without decimals:")
        self.matkaInput = QLineEdit()
        self.matkaInput.textChanged.connect(lambda: self.input_checker(self.matkaInput.text(), "d"))
        matkaLayer.addWidget(self.matkaLabel)
        matkaLayer.addWidget(self.matkaInput)

        buttonLayer = QHBoxLayout()
        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(lambda: self.switch_view.emit(0))
        self.submitButton = QPushButton("Save")
        self.submitButton.clicked.connect(lambda: self.save_handler(self.dateInput.text(), self.timeInput.text(), self.matkaInput.text()))
        self.submitButton.setDisabled(True)
        buttonLayer.addWidget(self.backButton)
        buttonLayer.addWidget(self.submitButton)

        layout.addLayout(dateLayer)
        layout.addLayout(timeLayer)
        layout.addLayout(matkaLayer)
        layout.addLayout(buttonLayer)

    def save_handler(self, date, time, distance):
        save_to_file("sessions.txt", "a", f"{date}-{time}-{distance}-{calculate_calories(get_file_content("physique.txt"), distance)}\n")
        self.dateInput.setText("")
        self.timeInput.setText("")
        self.matkaInput.setText("")
        self.switch_view.emit(0)

    def input_checker(self, candidate, mode):
        if check_input(candidate, mode):
            for i in self.inputChecker:
                if i[0] == mode:
                    i[1] = True
            if self.inputChecker[0][1] and self.inputChecker[1][1] and self.inputChecker[2][1]:
                self.submitButton.setEnabled(True)
        else:
            for i in self.inputChecker:
                if i[0] == mode:
                    i[1] = False
            self.submitButton.setDisabled(True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Activity Tracker - PATapp")
        self.setMinimumSize(QSize(600, 300))
        self.setMaximumSize(QSize(1200, 900))
        self.move(600, 300)

        self.stack = QStackedWidget()
        self.menuview = Menu()
        self.menuview.switch_view.connect(self.stack.setCurrentIndex)
        self.newseshview = AddSession()
        self.newseshview.switch_view.connect(self.stack.setCurrentIndex)
        self.physiqueview = Physique()
        self.physiqueview.switch_view.connect(self.stack.setCurrentIndex)
        self.sessionsview = ShowSessions()
        self.sessionsview.switch_view.connect(self.stack.setCurrentIndex)
        self.graphsview = DrawGraphs()
        self.graphsview.switch_view.connect(self.stack.setCurrentIndex)

        self.stack.addWidget(self.menuview)     #0
        self.stack.addWidget(self.newseshview)  #1
        self.stack.addWidget(self.physiqueview) #2
        self.stack.addWidget(self.sessionsview) #3
        self.stack.addWidget(self.graphsview)   #4
        self.stack.setCurrentIndex(0)
        self.setCentralWidget(self.stack)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
    #cli_menu()
