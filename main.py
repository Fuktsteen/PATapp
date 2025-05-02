# Code for the Personal Activity Tracker, PATapp.

from PyQt5.QtCore import QSize, pyqtSignal, Qt, QUrl, center
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QStackedWidget, QLineEdit, \
    QHBoxLayout, QLabel, QRadioButton, QButtonGroup
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
    return round(calories, 2)

def calculate_pace(distance, duration):
    # returns average pace for a session in km/h = distance / duration
    raw_time = duration.split(":")
    time = int(raw_time[0]) + int(raw_time[1]) / 60 + int(raw_time[2]) / 3600
    return round((int(distance)/1000) / time, 2)

def calculate_monthly_exercises():
    # raw_data = [ [detail, detail, ... ] [detail, detail, ... ] ... ]
    # monthly_amounts = number of exercises for each month
    raw_data = fetch_session_details()
    monthly_amounts = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
    for session in raw_data:
        kuukausi = session[0].split(".")[1]
        monthly_amounts[int(kuukausi)-1] += 1
    return monthly_amounts

def check_input(input, mode):
    if input.strip() == "":
        return False
    elif mode == "d":
        try:
            if int(input) < 0:
                raise ValueError
            return True
        except ValueError:
            return False
    elif mode == "physique":
        try:
            if int(input.strip()) < 0:
                raise ValueError
        except ValueError:
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
            #print(f"Invalid input.")
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
        self.ibw_calculator = QPushButton("IBW Calculator")
        self.githubButton = QPushButton("GitHub")
        self.exit_button = QPushButton("Exit")
        self.calory_info = QLabel()

        self.draw_graphs.clicked.connect(lambda: self.switch_view.emit(4))
        self.new_session.clicked.connect(lambda: self.switch_view.emit(1))
        self.edit_session.clicked.connect(lambda: self.switch_view.emit(3))
        self.replace_physique.clicked.connect(lambda: self.switch_view.emit(2))
        self.ibw_calculator.clicked.connect(lambda: self.switch_view.emit(5))
        self.githubButton.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/Fuktsteen/PATapp")))
        self.exit_button.clicked.connect(lambda: exit())
        layout.addWidget(self.draw_graphs)
        layout.addWidget(self.new_session)
        layout.addWidget(self.edit_session)
        layout.addWidget(self.replace_physique)
        layout.addWidget(self.ibw_calculator)
        layout.addWidget(self.githubButton)
        layout.addWidget(self.exit_button)
        layout.addWidget(self.calory_info)

    def get_calory_info(self):
        # ACSM recommendation:
        # minimum  1000 kcal / week
        # fat loss 2000-3000 kcal / week
        raw_sessions = fetch_session_details()
        calories = 0
        session_counter = 0
        try:
            for i in list(range(1,6)):
                calories += calculate_calories(raw_sessions[i*(-1)][3], raw_sessions[i*(-1)][2])
                session_counter += 1
        except IndexError:
            pass
        if session_counter == 0:
            return (f"Save sessions to view average burnt calories here."
                    f"\nBurn 1000 kcal/week to upkeep basic health"
                    f"\nBurn 2000-3000 kcal/week to lose fat"
                    f"\n(ACSM recommendation)")
        calorie_average = calories / session_counter
        minimi = int(round(1000 / calorie_average, 0))
        laihutus_down = int(round(2000 / calorie_average, 0))
        laihutus_up = int(round(3000 / calorie_average, 0))
        return (f"Average calories burnt during last {session_counter} sessions: {int(round(calorie_average, 0))} kcal" 
                f"\nExercise weekly:"
                f"\n{minimi} times at minimum to upkeep basic health by burning 1000 kcal/week"
                f"\n{laihutus_down}-{laihutus_up} times if trying to lose fat to burn 2000-3000 kcal/week"
                f"\n(ACSM recommendation)")

    def showEvent(self, event):
        self.window().resize(500, 300)
        self.calory_info.setText(self.get_calory_info())
        self.edit_session.setText(f"Show session details ({len(fetch_session_details())} saved sessions)")
        if get_file_content("physique.txt") != "":
            self.replace_physique.setText(f"Replace existing physique ({get_file_content("physique.txt")} kg)")
        else:
            self.replace_physique.setText(f"SET PHYSIQUE")
        super().showEvent(event)

class IBWcalculator(QWidget):
    switch_view = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(500)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        self.backButton = QPushButton("Back")
        self.backButton.clicked.connect(lambda: self.switch_view.emit(0))
        self.infoLabel = QLabel("Calculate your ideal body weight using the Devine Formula.")
        self.resultLabel = QLabel("Waiting for valid input.")
        self.resultLabel.setAlignment(Qt.AlignHCenter)

        genderLayer = QHBoxLayout()
        self.genderLabel = QLabel("Gender:")
        self.maleButton = QRadioButton("M")
        self.femaleButton = QRadioButton("F")
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.maleButton)
        self.buttonGroup.addButton(self.femaleButton)
        self.buttonGroup.buttonClicked.connect(lambda: self.result_maker(self.heightInput.text()))
        genderLayer.addWidget(self.genderLabel)
        genderLayer.addWidget(self.maleButton)
        genderLayer.addWidget(self.femaleButton)

        heightLayer = QHBoxLayout()
        self.heightLabel = QLabel("Height in cm:")
        self.heightInput = QLineEdit()
        self.heightInput.textChanged.connect(lambda: self.result_maker(self.heightInput.text()))
        heightLayer.addWidget(self.heightLabel)
        heightLayer.addWidget(self.heightInput)

        layout.addWidget(self.backButton)
        layout.addWidget(self.infoLabel)
        layout.addLayout(genderLayer)
        layout.addLayout(heightLayer)
        layout.addWidget(self.resultLabel)

    def result_maker(self, candidate):
        weight = get_file_content("physique.txt")
        try:
            if self.maleButton.isChecked():
                paino_vakio = 50
            elif self.femaleButton.isChecked():
                paino_vakio = 45.5
            else:
                raise ValueError
            ideal_weight = round(paino_vakio + 2.3 * ( int(candidate)/2.54 - 60 ), 1)
            if weight != "":
                weight_info = f"\nYour weight ({weight} kg) is off the ideal by {round(int(weight)-ideal_weight, 1)} kg"
            else:
                weight_info = ""
            self.resultLabel.setText(f"Your ideal body weight is {ideal_weight} kg"
                                     f"{weight_info}")
        except ValueError:
            self.resultLabel.setText("Waiting for valid input.")

    def showEvent(self, event):
        self.heightInput.setText("")
        super().showEvent(event)

class DrawGraphs(QWidget):
    switch_view = pyqtSignal(int)
    sessions_sorted = [ [], [], [], [], [], [] ]
    duration_minutes = []
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

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
        axDistance.plot(self.sessions_sorted[0], self.sessions_sorted[2], marker='o', linestyle='-', color='blue', linewidth=1)
        axDistance.set_ylabel('Distance (m)')
        axDistance.set_xlabel('Date')
        axDistance.grid(True, linestyle='--', alpha=0.5)
        axDistance.set_title("Distance Over Time")
        axDuration = self.dateDuration.figure.add_subplot(111)
        axDuration.plot(self.sessions_sorted[0], self.duration_minutes, marker='o', linestyle='-', color='blue', linewidth=1)
        axDuration.set_ylabel('Duration (min)')
        axDuration.set_xlabel('Date')
        axDuration.grid(True, linestyle='--', alpha=0.5)
        axDuration.set_title("Duration Over Time")
        axCalories = self.dateCalories.figure.add_subplot(111)
        axCalories.plot(self.sessions_sorted[0], self.sessions_sorted[5], marker='o', linestyle='-', color='blue', linewidth=1)
        axCalories.set_ylabel('Calories (kcal)')
        axCalories.set_xlabel('Date')
        axCalories.grid(True, linestyle='--', alpha=0.5)
        axCalories.set_title("Calories Burnt Over Time")
        axPace = self.datePace.figure.add_subplot(111)
        axPace.plot(self.sessions_sorted[0], self.sessions_sorted[4], marker='o', linestyle='-', color='blue', linewidth=1)
        axPace.set_ylabel('Pace (km/h)')
        axPace.set_xlabel('Date')
        axPace.grid(True, linestyle='--', alpha=0.5)
        axPace.set_title("Pace Over Time")

    def showEvent(self, event):
        self.window().resize(1400, 900)
        # self.sessions_sorted = [ [dates], [durations], [distances], [weights], [paces], [calories] ]
        # raw_sessions = [ [session], [session], ... ]
        # session = [ date, duration, distance, weight ]
        self.sessions_sorted = [ [], [], [], [], [], [] ]
        self.duration_minutes = []
        raw_sessions = fetch_session_details()
        for session in raw_sessions:
            for id, detail in enumerate(session):
                if id in [2, 3]:
                    self.sessions_sorted[id].append(float(detail))
                elif id == 0:
                    self.sessions_sorted[id].append(detail[:-2])
                elif id == 1:
                    self.sessions_sorted[id].append(detail)
                    broken_durations = detail.split(":") # hours : minutes : seconds
                    self.duration_minutes.append( int(broken_durations[1]) + int(broken_durations[2])/60 + int(broken_durations[0])*60 )
            self.sessions_sorted[4].append(calculate_pace(session[2], session[1]))
            # calculate_pace(session[2], session[1])
            self.sessions_sorted[5].append(calculate_calories(session[3], session[2]))
            # calculate_calories(session[3], session[2])
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
        self.sessionGraph = FigureCanvas(Figure())
        layout.addLayout(buttonLayer)
        layout.addLayout(inputLayer)
        layout.addWidget(self.sessionDetail)
        layout.addWidget(self.sessionGraph)

    def plot(self):
        self.sessionGraph.figure.clear()
        axSessions = self.sessionGraph.figure.add_subplot(111)
        months = list(range(1, 13))
        axSessions.plot(months, calculate_monthly_exercises(), marker='o', linestyle='-', color='blue', linewidth=1)
        axSessions.set_title("Amount Exercised By Month")
        axSessions.set_xticks(months)
        axSessions.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        axSessions.grid(True, linestyle='--', alpha=0.5)

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
        self.window().resize(800, 600)
        self.session_data = fetch_session_details()
        self.tarkastaja = len(self.session_data)
        session_text = ""
        for id, session in enumerate(self.session_data):
            session_text += f"{id+1}.       Date: {session[0]}      Duration: {session[1]}      Distance: {session[2]}      Pace: {calculate_pace(session[2], session[1])}      Weight: {session[3]}      Burned calories: {calculate_calories(session[3], session[2])}\n"
        if session_text == "":
            self.sessionDetail.setAlignment(Qt.AlignCenter)
            session_text = f"No saved sessions."
        else:
            self.sessionDetail.setAlignment(Qt.AlignLeft)
        self.sessionDetail.setText(session_text)
        self.chooseInput.setText("")
        self.plot()
        self.sessionGraph.draw()
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
        paino = get_file_content('physique.txt')
        if paino == "":
            paino = 0
        self.infoLabel.setText(f"Your current saved physique is {paino} kg."
                                f"\nThis is used to estimate burned calories based on distance exercised:"
                                f"\nCalories burned ≈ body mass (kg) × distance (km) × 1 kcal·kg⁻¹·km⁻¹")
        self.physiqueInput.setText("")
        super().showEvent(event)

    def save_handler(self, weight):
        save_to_file("physique.txt", "w", weight)
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

    def showEvent(self, event):
        if get_file_content("physique.txt") == "":
            self.submitButton.setText("SET PHYSIQUE TO SAVE SESSIONS!")
            self.submitButton.setStyleSheet("color: red;")
        else:
            self.submitButton.setText("Save")
            self.submitButton.setStyleSheet("color: black;")
        self.dateInput.setText("")
        self.timeInput.setText("")
        self.matkaInput.setText("")
        super().showEvent(event)

    def save_handler(self, date, time, distance):
        weight = get_file_content("physique.txt")
        save_to_file("sessions.txt", "a", f"{date}-{time}-{distance}-{weight}\n")
        self.switch_view.emit(3)

    def input_checker(self, candidate, mode):
        if check_input(candidate, mode):
            for i in self.inputChecker:
                if i[0] == mode:
                    i[1] = True
            if self.inputChecker[0][1] and self.inputChecker[1][1] and self.inputChecker[2][1] and get_file_content("physique.txt") != "":
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
        self.setMinimumSize(QSize(500, 230))
        self.move(100, 100)

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
        self.ibwview = IBWcalculator()
        self.ibwview.switch_view.connect(self.stack.setCurrentIndex)

        self.stack.addWidget(self.menuview)     #0
        self.stack.addWidget(self.newseshview)  #1
        self.stack.addWidget(self.physiqueview) #2
        self.stack.addWidget(self.sessionsview) #3
        self.stack.addWidget(self.graphsview)   #4
        self.stack.addWidget(self.ibwview)      #5
        self.stack.setCurrentIndex(0)
        self.setCentralWidget(self.stack)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
