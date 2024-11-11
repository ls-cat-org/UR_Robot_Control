import sys, os, rtde_receive
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtCore import Qt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from DataFiles.Var_LSCAT import RoIp

ROBOT_IP = RoIp

class RobotControlGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.robot_position = None
        self.robot = rtde_receive.RTDEReceiveInterface(ROBOT_IP)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Save UR3e Position Interface")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.position_label = QLabel(self)
        layout.addWidget(self.position_label)

        button_capture_position = QPushButton("Capture Current Position")
        button_capture_position.clicked.connect(self.capture_position)
        layout.addWidget(button_capture_position)

        self.save_position_textbox = QLineEdit(self)
        self.save_position_textbox.setPlaceholderText("Enter variable name to save position")
        layout.addWidget(self.save_position_textbox)

        button_save_position = QPushButton("Save Position as Variable")
        button_save_position.clicked.connect(self.save_position_as_variable)
        layout.addWidget(button_save_position)

    def capture_position(self):
        try:
            # Get the current robot position (in meters and radians) using rtde_control
            current_pose = self.robot.getActualTCPPose()
            self.robot_position = [round(coord, 3) for coord in current_pose]
            self.position_label.setText(f"Current Position: {self.robot_position}")
        except Exception as e:
            print(f"Error: Unable to capture robot position: {e}")

    def save_position_as_variable(self):
        variable_name = self.save_position_textbox.text()

        if self.robot_position and variable_name:
            try:
                # Save the variable to a file
                with open("Var_LSCAT.py", "a") as file:
                    file.write(f"{variable_name} = {self.robot_position}\n")
                print(f"Position saved as variable '{variable_name}' in Var.py")
            except Exception as e:
                print(f"Error: Unable to save position as variable: {e}")
        else:
            print("Error: Please capture the position and enter a variable name first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotControlGUI()
    window.show()
    sys.exit(app.exec())
