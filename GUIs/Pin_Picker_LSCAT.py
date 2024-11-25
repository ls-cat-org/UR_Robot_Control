import sys, copy, time, json, epics, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import DataFiles.Var_LSCAT as Var_LSCAT
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

        self.load_pvs()


    def log(self, message):
        #Append a message to the log box
        self.log_box.append(message)

    def populate_lists(self):
        selected_puck_name = self.puck_combo.currentText()
        if selected_puck_name != "Select a Puck":
            selected_puck = next((puck for puck in self.data if puck["Puck Name"] == selected_puck_name), None)
            if selected_puck:
                self.pin_positions = selected_puck["Pin Positions"]
                pins = list(self.pin_positions.keys())
                self.pin_combo.clear()
                self.pin_combo.addItem("Select a Pin")
                self.pin_combo.addItems(pins)
                print(pins)
                print("Noodles")

    def load_pvs(self):
        filename = os.path.join("DataFiles", "PV_config.json")
        with open(filename, 'r') as file:
            self.pvs = json.load(file)
            self.log("Populated Available PVs")
         
    def select_pin(self):
        self.selected_pin_name = self.pin_combo.currentText()
        if self.selected_pin_name != "Select a Pin":
            self.selected_pin = self.pin_positions.get(self.selected_pin_name, "Error: Something is wrong :(")


            if self.selected_pin != "Error: Something is wrong :(":
                # Assuming 'self.selected_pin' holds the pin number or some related data
                # Create the string 'PuckName,PinNumber'
                selected_puck_name = self.puck_combo.currentText()
                pin_number = self.selected_pin_name.split('_')[-1] # The pin name is used here as the pin number (adjust as needed)
                
                # Combine the puck name and pin number
                self.puck_pin_string = f"{selected_puck_name},{pin_number}"

                # Here you can upload puck_pin_string to the PV or use it as needed
                print(f"Selected Puck and Pin for upload: {self.puck_pin_string}")

            else:
                print("Error: Invalid pin selection.")


    def mount_pin(self):
        Sample_to_Mount = self.pvs.get('Sample To Mount')
        Sample_PV = epics.PV(f'{Sample_to_Mount}')
        Sample_PV.put(f'{self.puck_pin_string}')
        Mount_Sample = self.pvs.get('Mount Sample')
        Mount_PV = epics.PV(f'{Mount_Sample}')
        Mount_PV.put(1)


    def dismount_pin(self):
        Dismount_Sample = self.pvs.get('Dismount Sample')
        Dismount_PV = epics.PV(f'{Dismount_Sample}')
        Dismount_PV.put(1)

    def exchange_pin(self):
        Exchange = self.pvs.get("Exchange Sample")
        Ex_PV = epics.PV(f'{Exchange}')
        Ex_PV.put(1)

    def go_to_wait(self):
        Wait = self.pvs.get('Go Home')
        Wait_PV = epics.PV(f'{Wait}')
        Wait_PV.put(1)

    def quit(self):
        print("Later, Ya'll!1")


def main():
    file_path = os.path.abspath(os.path.join("DataFiles", "Puck_Data.json"))
    with open(file_path, "r") as file:
        data = json.load(file)

    app = QApplication(sys.argv)
    window = PuckSelector(data)
    app.aboutToQuit.connect(window.quit)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
