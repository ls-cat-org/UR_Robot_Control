import sys, copy, time, json, epics
import Var_LSCAT, MX_Robot
from LS_Robot_Classes import Robot_Control
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QTextEdit

class PuckSelector(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("Puck Selector")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.puck_combo = QComboBox()
        self.puck_combo.addItem("Select a Puck")
        for puck in self.data:
            self.puck_combo.addItem(puck["Puck Name"])
        self.puck_combo.currentIndexChanged.connect(self.populate_lists)
        layout.addWidget(self.puck_combo)

                # Create a log box
        self.log_box = QTextEdit(self)
        self.log_box.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.log_box)

        self.pin_combo = QComboBox()
        self.pin_combo.addItem("Select a Pin")
        self.pin_combo.currentIndexChanged.connect(self.select_pin)
        layout.addWidget(self.pin_combo)

        # Add Mount Selected Pin button
        self.mount_button = QPushButton("Mount Selected Pin")
        self.mount_button.clicked.connect(self.mount_pin)
        layout.addWidget(self.mount_button)

        # Add Dismount Selected Pin button
        self.dismount_button = QPushButton("Dismount Selected Pin")
        self.dismount_button.clicked.connect(self.dismount_pin)
        layout.addWidget(self.dismount_button)

        # Add Exchange With Selected Pin button
        self.exchange_button = QPushButton("Exchange With Selected Pin")
        self.exchange_button.clicked.connect(self.exchange_pin)
        layout.addWidget(self.exchange_button)

        # Add Go to Wait button
        self.wait_button = QPushButton("Go to Wait")
        self.wait_button.clicked.connect(self.go_to_wait)
        layout.addWidget(self.wait_button)

        self.setLayout(layout)

        self.robot = Robot_Control(Var_LSCAT.RoIp)
        self.pvs = {}

    def log(self, message):
        #Append a message to the log box
        self.log_box.append(message)

    def populate_lists(self):
        selected_puck_name = self.puck_combo.currentText()
        if selected_puck_name != "Select a Puck":
            self.selected_puck = next((puck for puck in self.data if puck["Puck Name"] == selected_puck_name), None)
            if self.selected_puck:
                self.pin_positions = self.selected_puck["Pin Positions"]
                pins = list(self.pin_positions.keys())
                self.pin_combo.clear()
                self.pin_combo.addItem("Select a Pin")
                self.pin_combo.addItems(pins)
                print(pins)
                print("Noodles")
         
    def select_pin(self):
        self.selected_pin_name = self.pin_combo.currentText()
        if self.selected_pin_name != "Select a Pin":
            self.selected_pin = self.pin_positions.get(self.selected_pin_name, "Error: Something is wrong :(")
            print(self.selected_pin_name)
            print(self.selected_pin)

    def mount_pin(self):
        sample_string = f"{self.selected_puck},{self.selected_pin}"
        epics.caput('UR5:SampleToMount', sample_string)

        MX_Robot.mount_pin()
        self.log('Updated CurrentSample PV')

    def dismount_pin(self):
        MX_Robot.dismount_pin()

    def exchange_pin(self):
        MX_Robot.exchage_pin()

    def go_to_wait(self):
        MX_Robot.go_to_wait()

def main():
    with open("Puck_Data.json", "r") as file:
        data = json.load(file)

    app = QApplication(sys.argv)
    window = PuckSelector(data)
    app.aboutToQuit.connect(window.quit)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
