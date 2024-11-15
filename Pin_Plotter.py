import sys, math, statistics, json, rtde_receive
import DataFiles.Var_LSCAT as Var_LSCAT
from dataclasses import dataclass
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton


def find_circle_center(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    Ux = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / D
    Uy = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / D

    angle = math.atan2(y1 - Uy, x1 - Ux)
    angle_degrees = math.degrees(angle)

    if angle_degrees < 0:
        angle_degrees = 360 + angle_degrees
        print(f"Angle sign adjusted for mathin'")

    return (Ux, Uy), angle_degrees

class CircleCenterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pin Plotter")
        self.setGeometry(100, 100, 500, 350)  # Adjusted window width

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Add a text input box for "Puck Name"
        self.puck_name_layout = QHBoxLayout()
        self.puck_name_label = QLabel("Puck Name:")
        self.puck_name_edit = QLineEdit()
        self.puck_name_layout.addWidget(self.puck_name_label)
        self.puck_name_layout.addWidget(self.puck_name_edit)

        self.point1_layout = QHBoxLayout()  # Create a horizontal layout for Point 1
        self.point1_label = QLabel("Point 1:")
        self.point1_edit = QLineEdit()
        self.capture_button_1 = QPushButton("Capture")
        self.capture_button_1.clicked.connect(self.capture_position_1)
        self.point1_layout.addWidget(self.point1_label)
        self.point1_layout.addWidget(self.point1_edit)
        self.point1_layout.addWidget(self.capture_button_1)

        self.point2_layout = QHBoxLayout()  # Create a horizontal layout for Point 2
        self.point2_label = QLabel("Point 2:")
        self.point2_edit = QLineEdit()
        self.capture_button_2 = QPushButton("Capture")
        self.capture_button_2.clicked.connect(self.capture_position_2)
        self.point2_layout.addWidget(self.point2_label)
        self.point2_layout.addWidget(self.point2_edit)
        self.point2_layout.addWidget(self.capture_button_2)

        self.point3_layout = QHBoxLayout()  # Create a horizontal layout for Point 3
        self.point3_label = QLabel("Point 3:")
        self.point3_edit = QLineEdit()
        self.capture_button_3 = QPushButton("Capture")
        self.capture_button_3.clicked.connect(self.capture_position_3)
        self.point3_layout.addWidget(self.point3_label)
        self.point3_layout.addWidget(self.point3_edit)
        self.point3_layout.addWidget(self.capture_button_3)

        self.layout.addLayout(self.puck_name_layout)
        self.layout.addLayout(self.point1_layout)
        self.layout.addLayout(self.point2_layout)
        self.layout.addLayout(self.point3_layout)
        self.calculate_button = QPushButton("Calculate Puck Center and Angle")
        self.calculate_button.clicked.connect(self.calculate_circle_center)
        self.layout.addWidget(self.calculate_button)

        self.result_label = QLabel()
        self.layout.addWidget(self.result_label)

        self.perform_action_button = QPushButton("Calculate Pin Positions")
        self.perform_action_button.clicked.connect(self.pin_calc)
        self.perform_action_button.setEnabled(False)  # Initially disabled
        self.layout.addWidget(self.perform_action_button)

        self.point_text_edit = QTextEdit()  # Large text box for 16 points
        self.point_text_edit.setPlaceholderText("16 Points will be displayed here")
        self.layout.addWidget(self.point_text_edit)

        self.central_widget.setLayout(self.layout)

        self.circle_center = None
        self.angle_degrees = None

    def capture_position_1(self):
        self.Robot = rtde_receive.RTDEReceiveInterface(Var_LSCAT.RoIp)
        TCP = self.Robot.getActualTCPPose()
        self.TCP = [round(coord, 3) for coord in TCP]
        point1_values_str = ', '.join(map(str, self.TCP))
        self.point1_edit.setText(point1_values_str)
        self.Robot.disconnect()

    def capture_position_2(self):
        self.Robot = rtde_receive.RTDEReceiveInterface(Var_LSCAT.RoIp)
        TCP = self.Robot.getActualTCPPose()
        self.TCP = [round(coord, 3) for coord in TCP]
        point2_values_str = ', '.join(map(str, self.TCP))

        # Set the formatted string to point1_edit
        self.point2_edit.setText(point2_values_str)
        self.Robot.disconnect()

    def capture_position_3(self):
        self.Robot = rtde_receive.RTDEReceiveInterface(Var_LSCAT.RoIp)
        TCP = self.Robot.getActualTCPPose()
        self.TCP = [round(coord, 3) for coord in TCP]
        point3_values_str = ', '.join(map(str, self.TCP))

        # Set the formatted string to point1_edit
        self.point3_edit.setText(point3_values_str)
        self.Robot.disconnect()

    def calculate_circle_center(self):

        pin1_str = self.point1_edit.text().split(",")
        pin2_str = self.point2_edit.text().split(",")
        pin3_str = self.point3_edit.text().split(",")

        if len(pin1_str) == 6 and len(pin2_str) == 6 and len(pin3_str) == 6:
            self.pin1 = [float(value) for value in pin1_str]
            self.pin2 = [float(value) for value in pin2_str]
            self.pin3 = [float(value) for value in pin3_str]

            x1, y1 = self.pin1[0], self.pin1[1]
            x2, y2 = self.pin2[0], self.pin2[1]
            x3, y3 = self.pin3[0], self.pin3[1]

            center, angle_degrees = find_circle_center((x1, y1), (x2, y2), (x3, y3))

            self.circle_center = center
            self.angle_degrees = angle_degrees

            result_text = f"Circle Center: ({center[0]:.4f}, {center[1]:.4f})\nAngle (degrees): {angle_degrees:.4f}"
            self.result_label.setText(result_text)

            self.perform_action_button.setEnabled(True)  # Enable the action button
        else:
            print("Error: Each input should contain 6 values separated by commas.")

    def pin_calc(self):

        self.z_vals = [self.pin1[2], self.pin2[2], self.pin3[2]]
        self.z_avg = statistics.mean(self.z_vals)
        self.Puck_Name = self.puck_name_edit.text()
        self.puck_center = [round(self.circle_center[0], 3), round(self.circle_center[1], 3), round(self.z_avg, 3), 2.236, 2.2, 0.0]
        print(self.puck_center)

        if self.circle_center is not None and self.angle_degrees is not None:

            radius1 = .01212  # Radius for points 1-5
            radius2 = .026310  # Radius for points 6-11
            start_angle_radians = math.radians(self.angle_degrees)
            
            points = []
            Pin_Positions = []

            # Generate points 1-5
            for i in range(1, 6):
                angle = start_angle_radians + ((i - 1) * (2 * math.pi / 5))
                print(f"Angle {i}: {angle}")
                x = self.circle_center[0] + radius1 * math.cos(angle)
                y = self.circle_center[1] + radius1 * math.sin(angle)
                new_values = [round(x, 3), round(y, 3), round(self.z_avg, 3), 2.25, 2.192, 0.0]
                points.append(f"Point {i}: {new_values}")
                #print(f"Point {i}: {new_values}")
                Pin_Positions.append(new_values)


            # Generate points 6-16
            for i in range(6, 17):
                angle = start_angle_radians + ((i - 6) * (2 * math.pi / 11))
                print(f"Angle {i}: {angle}")
                x = self.circle_center[0] + radius2 * math.cos(angle)
                y = self.circle_center[1] + radius2 * math.sin(angle)              
                new_values = [round(x, 3), round(y, 3), round(self.z_avg, 3), 2.25, 2.192, 0.0]
                points.append(f"Point {i}: {new_values}")
                #print(f"Point {i}: {new_values}")
                Pin_Positions.append(new_values)

            self.point_text_edit.setPlainText("\n".join(points))
            
            def custom_serialize(data):
                def process_dict(d, indent_level=0):
                    result = "{\n"
                    for key, value in d.items():
                        if isinstance(value, list):
                            result += ' ' * (indent_level + 4) + f'"{key}": {json.dumps(value)},\n'
                        else:
                            if isinstance(value, dict):
                                result += ' ' * (indent_level + 4) + f'"{key}": {process_dict(value, indent_level + 4)},\n'
                            else:
                                result += ' ' * (indent_level + 4) + f'"{key}": {json.dumps(value)},\n'
                    result = result.rstrip(',\n') + "\n" + ' ' * (indent_level + 4) + "}"
                    return result

                data_block = process_dict(data)
                format_block = data_block + "\n]"
                final_block = ",\n\t" + format_block

                return final_block  
            
            roundeddegrees = round(self.angle_degrees, 3)

            data = {
                "Puck Name": self.Puck_Name,
                "Angle (degrees)": roundeddegrees,
                "Center Position": self.puck_center,
                "Pin Positions": {}  # Create a dictionary to store the 16 pin lists
            }

            for i, pin in enumerate(Pin_Positions, start=1):
                data["Pin Positions"][f"Pin_{i}"] = pin

            formatted_data = custom_serialize(data)

            with open("Puck_Data.json", "r") as json_file:
                old_data = json_file.readlines()
                old_data[-1] = old_data[-1][:-1]
                
            with open("Puck_Data.json", "w") as json_file:
                json_file.writelines(old_data)

            with open("Puck_Data.json", "a") as json_file:
                json_file.write(formatted_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircleCenterApp()
    window.show()
    sys.exit(app.exec())
