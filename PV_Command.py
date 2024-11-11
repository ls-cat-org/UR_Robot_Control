import sys, os
import json
from epics import PV, caget, caput
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from PyQt6.QtCore import Qt

# Load PV configurations from JSON file
def load_pvs(json_file):
    file_path = os.path.join("DataFiles", "MD3_PV_config.json")
    with open(file_path, 'r') as f:
        pv_data = json.load(f)
        print(pv_data)
    return {name: PV(address) for name, address in pv_data.items()}

# Initialize the PVs
pvs = load_pvs('file.json')

class PVControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PV Command")
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

        self.get_position = QPushButton("Get Position from PV")
        self.get_position.clicked.connect(self.get_pose)
        layout.addWidget(self.get_position)
        
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

        pv_name = self.pv_dropdown.currentText()
        pv = pvs.get(pv_name)
    

        if pv:
            # Retrieve the value of the PV using caget
            value = caget(pv.pvname)
            
            # Check if the value is numeric or a string
            if isinstance(value, (int, float)):
                # If numeric, display it as is
                self.output_display.setText(f"{pv_name}: {value}")
            elif isinstance(value, str):
                # If the value is a string, display it as is
                self.output_display.setText(f"{pv_name}: '{value}'")
            else:
                # For other types, convert to string
                self.output_display.setText(f"{pv_name}: {str(value)}")
        else:
            self.output_display.setText("Invalid PV selected.")


    def send_caput(self):
        """Send a caput command to the selected PV."""
        pv_name = self.pv_dropdown.currentText()
        pv = pvs.get(pv_name)
        
        if pv:
            value = self.caput_entry.text()
            
            # Check if the value is wrapped in quotes (either single or double)
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                # Remove the quotes and send as string
                value = value[1:-1]
                caput(pv.pvname, value)
                self.output_display.append(f"{pv_name}: '{value}'")
            else:
                # Try to convert the value to a numeric type (int or float)
                try:
                    numeric_value = float(value)
                    # If it's an integer, convert to int; otherwise, keep it as float
                    if numeric_value.is_integer():
                        numeric_value = int(numeric_value)
                    caput(pv.pvname, numeric_value)
                    self.output_display.append(f"{pv_name}: {numeric_value}")
                except ValueError:
                    self.output_display.append("Invalid input. Please enter a valid numeric or string value.")
        else:
            self.output_display.append("No PV selected.")

            
    def get_pose(self):
        pv_name = self.pv_dropdown.currentText()
        print(f"Selected PV for pose: {pv_name}")  # Debugging print
        pv = pvs.get(pv_name)

        if pv:
            # Retrieve the value of the PV using caget
            value = caget(pv.pvname)
            print(f"Retrieved PV value: {value}")  # Debugging print

            # Check if the value is None or not in the expected format
            if value is None:
                self.output_display.setText(f"Error: Unable to retrieve value from PV '{pv.pvname}'.")
                return None

            try:
                # Split the PV value to get puck and pin information
                if "," in value:
                    puck, pin_str = value.split(",")
                    pin = int(pin_str)  # Convert pin number to integer

                    # Load the JSON file with puck and pin position data
                    file_path = os.path.join("DataFiles", "Puck_Data.json")
                    with open(file_path, 'r') as f:
                        position_data = json.load(f)

                    # Look for the puck name in the position data
                    for puck_data in position_data:
                        if puck_data.get("Puck Name") == puck:
                            pin_key = f"Pin_{pin}"
                            position = puck_data["Pin Positions"].get(pin_key)
                            
                            if position:
                                self.output_display.setText(f"Position for {puck}, Pin {pin}: {position}")
                                print(f"Position found for {puck} - {pin_key}: {position}")  # Debugging print
                                return position
                            else:
                                print(f"{pin_key} not found in Pin Positions for puck {puck}.")  # Debugging print
                                self.output_display.setText(f"Position data not found for puck {puck}, pin {pin}.")
                                return None
                    self.output_display.setText(f"No matching puck found in JSON data for '{puck}'.")
                    return None
                else:
                    self.output_display.setText(f"Invalid format in PV value '{value}'. Expected 'PuckName,PinNumber'.")
                    return None

            except ValueError as ve:
                self.output_display.setText(f"Error parsing pin number from '{value}': {ve}")
                return None
            except FileNotFoundError:
                self.output_display.setText("Error: Position data JSON file not found.")
                return None
            except json.JSONDecodeError:
                self.output_display.setText("Error: Failed to decode the position data JSON file.")
                return None
            except Exception as e:
                self.output_display.setText(f"Unexpected error occurred: {e}")
                return None
        else:
            self.output_display.setText("Invalid PV selected.")
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PVControlGUI()
    gui.show()
    sys.exit(app.exec())