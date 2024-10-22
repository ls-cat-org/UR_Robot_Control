import Var_LSCAT, sys
from LS_Robot_Classes import Robot_Control
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton

class GripperMount(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gripper Mounting")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()
        self.puck_combo = QComboBox()
        self.puck_combo = QComboBox()
        self.puck_combo.addItem("Select a Puck")

        # Add Mount Selected Pin button
        self.mount_button = QPushButton("Mount")
        self.mount_button.clicked.connect(self.Mount_Gripper)
        layout.addWidget(self.mount_button)

        # Add Dismount Selected Pin button
        self.dismount_button = QPushButton("Dismount")
        self.dismount_button.clicked.connect(self.Dismount_Gripper)
        layout.addWidget(self.dismount_button)

        # Add Go to Wait button
        self.wait_button = QPushButton("Go to Wait")
        self.wait_button.clicked.connect(self.Wait)
        layout.addWidget(self.wait_button)

        self.setLayout(layout)
        self.robot = Robot_Control(Var_LSCAT.RoIp)

    def Mount_Gripper(self):
        self.robot.Gripper_Swap("Mount")

    def Dismount_Gripper(self):
        self.robot.Gripper_Swap("Dismount")

    def Wait(self):
        self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, 0.75, 0.75)

    def quit(self):
        self.robot.Disconnect()
        print("Later, Ya'll!1")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GripperMount()
    window.show()
    sys.exit(app.exec())

