import sys
import json
from epics import PV, caget, caput
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from PyQt6.QtCore import Qt

# Load PV configurations from JSON file
def load_pvs(json_file):
    with open(json_file, 'r') as f:
        pv_data = json.load(f)
    return {name: PV(address) for name, address in pv_data.items()}

# Initialize the PVs
pvs = load_pvs("MD3_PV_config.json")

class PVControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PV Control GUI")
        self.setGeometry(300, 300, 400, 300)
        
        # Layout
        layout = QVBoxLayout()
        
        # PV Dropdown (QComboBox)
        self.pv_dropdown = QComboBox()
        self.pv_dropdown.addItems(pvs.keys())
        layout.addWidget(QLabel("Select PV:"))
        layout.addWidget(self.pv_dropdown)
        
        # Button to send caget command
        self.caget_button = QPushButton("Send Caget")
        self.caget_button.clicked.connect(self.get_caget_value)
        layout.addWidget(self.caget_button)
        
        # Entry for caput command
        self.caput_entry = QLineEdit()
        self.caput_entry.setPlaceholderText("Enter value to caput")
        layout.addWidget(QLabel("Caput Value:"))
        layout.addWidget(self.caput_entry)
        
        # Button to send caput command
        self.caput_button = QPushButton("Send Caput")
        self.caput_button.clicked.connect(self.send_caput)
        layout.addWidget(self.caput_button)
        
        # Output box for caget command
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output_display)
        
        self.setLayout(layout)
    
    def get_caget_value(self):
        """Retrieve and display the current value of the selected PV."""
        pv_name = self.pv_dropdown.currentText()
        pv = pvs.get(pv_name)
        if pv:
            value = caget(pv.pvname)
            self.output_display.setText(f"{pv_name}: {value}")
        else:
            self.output_display.setText("Invalid PV selected.")

    def send_caput(self):
        """Send a caput command to the selected PV."""
        pv_name = self.pv_dropdown.currentText()
        pv = pvs.get(pv_name)
        if pv:
            try:
                value = float(self.caput_entry.text())
                caput(pv.pvname, value)
                self.output_display.append(f"{pv_name}: {value}")
            except ValueError:
                self.output_display.append("Invalid input for caput. Please enter a numeric value.")
        else:
            self.output_display.append("No PV selected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PVControlGUI()
    gui.show()
    sys.exit(app.exec())