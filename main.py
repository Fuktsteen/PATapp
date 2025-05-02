# Code for the Personal Activity Tracker, PATapp.

from PyQt5.QtCore import QSize, pyqtSignal, Qt, QUrl, center
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QStackedWidget, QLineEdit, \
    QHBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def save_to_file(file, mode, details):
    with open(file, mode) as f:
        f.write(details)
    print(f"Saved!")

def get_file_content(file):
    with open(file) as f:
        content = f.read()
        return content

def calculate_calories(weight, distance):
    # Calories burned ≈ body mass (kg) × distance (km) × 1 kcal·kg⁻¹·km⁻¹
    calories = int(weight) * (int(distance) / 1000)
    print(f"\t{weight} kg * {int(distance) / 1000} km * 1 kcal*kg^(-1)*km^(-1) = {calories}")
    return round(calories, 2)

def calculate_pace(distance, duration):
    # returns average pace for a session in km/h = distance / duration
    raw_time = duration.split(":")
    time = int(raw_time[0]) + int(raw_time[1]) / 60 + int(raw_time[2]) / 3600
    return round((int(distance)/1000) / time, 2)

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

def fetch_session_details():
    raw_sessions = get_file_content("sessions.txt")
    fine_sessions = []
    session_data = raw_sessions.split("\n")
    for raw_session in session_data:
        fine_sessions.append(raw_session.split("-"))
    fine_sessions.pop()
    # fine_sessions = [ [detail, detail, ... ] [detail, detail, ... ] ... ]
    return fine_sessions

class Menu(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(500)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.draw_graphs = QPushButton("Draw graphs")
        self.new_session = QPushButton("Add new session details")
        self.edit_session = QPushButton()
        self.replace_physique = QPushButton()
        self.githubButton = QPushButton("GitHub")
        self.exit_button = QPushButton("Exit")

        self.draw_graphs.clicked.connect(lambda: self.switch_view.emit(4))
        self.new_session.clicked.connect(lambda: self.switch_view.emit(1))
        self.edit_session.clicked.connect(lambda: self.switch_view.emit(3))
        self.replace_physique.clicked.connect(lambda: self.switch_view.emit(2))
        self.githubButton.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Fuktsteen/PATapp")))
        self.exit_button.clicked.connect(lambda: exit())
        layout.addWidget(self.draw_graphs)
        layout.addWidget(self.new_session)
        layout.addWidget(self.edit_session)
        layout.addWidget(self.replace_physique)
        layout.addWidget(self.githubButton)
        layout.addWidget(self.exit_button)

    def showEvent(self, event):
        self.window().resize(500, 200)
        self.edit_session.setText(f"Show session details ({len(fetch_session_details())} saved sessions)")
        self.replace_physique.setText(f"Replace existing physique ({get_file_content("physique.txt")} kg)")
        super().showEvent(event)

class DrawGraphs(QWidget):
    switch_view = pyqtSignal(int)
    sessions_sorted = [ [], [], [], [], [], [] ]
    duration_minutes = []
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        #layout.setAlignment(Qt.AlignTop)

        buttonLayer = QHBoxLayout()
        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(lambda: self.switch_view.emit(0))
        self.graphNote = QLabel("Note: Viewing graphs in fullscreen may make them easier to read")
        buttonLayer.addWidget(self.backButton)
        buttonLayer.addWidget(self.graphNote)
        buttonLayer.setAlignment(Qt.AlignHCenter)

        graphLayer = QHBoxLayout()
        self.dateDistance = FigureCanvas(Figure())
        self.dateDuration = FigureCanvas(Figure())
        graphLayer.addWidget(self.dateDistance)
        graphLayer.addWidget(self.dateDuration)

        lowerGraphs = QHBoxLayout()
        self.dateCalories = FigureCanvas(Figure())
        self.datePace = FigureCanvas(Figure())
        lowerGraphs.addWidget(self.dateCalories)
        lowerGraphs.addWidget(self.datePace)

        layout.addLayout(buttonLayer)
        layout.addLayout(graphLayer)
        layout.addLayout(lowerGraphs)

    def plot(self):
        self.dateDistance.figure.clear()
        self.dateDuration.figure.clear()
        self.dateCalories.figure.clear()
        self.datePace.figure.clear()
        axDistance = self.dateDistance.figure.add_subplot(111)
        axDistance.plot(self.sessions_sorted[0], self.sessions_sorted[2])
        axDistance.set_ylabel('Distance (m)')
        axDistance.set_xlabel('Date')
        axDuration = self.dateDuration.figure.add_subplot(111)
        axDuration.plot(self.sessions_sorted[0], self.duration_minutes)
        axDuration.set_ylabel('Duration (min)')
        axDuration.set_xlabel('Date')
        axCalories = self.dateCalories.figure.add_subplot(111)
        axCalories.plot(self.sessions_sorted[0], self.sessions_sorted[4])
        axCalories.set_ylabel('Calories (kcal)')
        axCalories.set_xlabel('Date')
        axPace = self.datePace.figure.add_subplot(111)
        axPace.plot(self.sessions_sorted[0], self.sessions_sorted[3])
        axPace.set_ylabel('Pace (km/h)')
        axPace.set_xlabel('Date')

    def showEvent(self, event):
        self.window().resize(1400, 900)
        # self.sessions_sorted = [ [dates], [durations], [distances], [paces], [calories], [weights] ]
        # raw_sessions = [ [session], [session], ... ]
        # session = [ date, duration, distance, pace, calories, weight ]
        self.sessions_sorted = [ [], [], [], [], [], [] ]
        self.duration_minutes = []
        raw_sessions = fetch_session_details()
        for session in raw_sessions:
            for id, detail in enumerate(session):
                if id in [2, 3, 4, 5]:
                    self.sessions_sorted[id].append(float(detail))
                elif id == 0:
                    self.sessions_sorted[id].append(detail[:-2])
                elif id == 1:
                    self.sessions_sorted[id].append(detail)
                    broken_durations = detail.split(":") # hours : minutes : seconds
                    self.duration_minutes.append( int(broken_durations[1]) + int(broken_durations[2])/60 + int(broken_durations[0])*60 )
        self.plot()
        self.dateDistance.draw()
        self.dateDuration.draw()
        self.dateCalories.draw()
        super().showEvent(event)

class ShowSessions(QWidget):
    switch_view = pyqtSignal(int)
    tarkastaja = 0
    session_data = []
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(800)
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
        self.session_data.pop(int(choice)-1)
        new_data = ""
        for session in self.session_data:
            for detail in session:
                new_data += f"{detail}-"
            new_data = new_data[:-1]
            new_data += "\n"
        save_to_file("sessions.txt", "w", new_data)
        self.switch_view.emit(0)
        self.switch_view.emit(3)

    def showEvent(self, event):
        self.window().resize(800, 500)
        self.session_data = fetch_session_details()
        self.tarkastaja = len(self.session_data)
        session_text = ""
        for id, session in enumerate(self.session_data):
            session_text += f"{id+1}.       Date: {session[0]}      Duration: {session[1]}      Distance: {session[2]}      Pace: {session[3]}      Weight: {session[5]}      Burned calories: {session[4]}\n"
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
        self.setMaximumWidth(500)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # need layers for info, input and buttons
        infoLayer = QHBoxLayout()
        self.infoLabel = QLabel()
        infoLayer.addWidget(self.infoLabel)
        infoLayer.setAlignment(Qt.AlignHCenter)

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
        self.setMaximumWidth(500)
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
        layout.addWidget(QLabel(f"NOTE\nAdded sessions aren't sorted in "
                                f"any way other than the order added, yet."
                                f"\nIt's possible to edit older sessions by accessing sessions.txt"))

    def save_handler(self, date, time, distance):
        weight = get_file_content("physique.txt")
        calories = calculate_calories(weight, distance)
        pace = calculate_pace(distance, time)
        save_to_file("sessions.txt", "a", f"{date}-{time}-{distance}-{pace}-{calories}-{weight}\n")
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
        self.setMinimumSize(QSize(500, 200))
        self.move(100, 200)

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
