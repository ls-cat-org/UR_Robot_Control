import sys, copy, time, json, epics, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import DataFiles.Var_LSCAT as Var_LSCAT
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
            selected_puck = next((puck for puck in self.data if puck["Puck Name"] == selected_puck_name), None)
            if selected_puck:
                self.pin_positions = selected_puck["Pin Positions"]
                pins = list(self.pin_positions.keys())
                self.pin_combo.clear()
                self.pin_combo.addItem("Select a Pin")
                self.pin_combo.addItems(pins)
                print(pins)
                print("Noodles")

    def load_pvs(self, filename='MD3_PV_config.json'):
        with open(filename, 'r') as file:
            self.pvs = json.load(filename)
            self.log("Populated Available PVs")
         
    def select_pin(self):
        self.selected_pin_name = self.pin_combo.currentText()
        if self.selected_pin_name != "Select a Pin":
            self.selected_pin = self.pin_positions.get(self.selected_pin_name, "Error: Something is wrong :(")
            print(self.selected_pin_name)
            print(self.selected_pin)

    def path_to_MD3(self):
        mount_offset = copy.deepcopy(Var_LSCAT.MX_Pin_Sample_Position)
        mount_offset[2] = 0.5
        speed = 2
        self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
        self.robot.Move_to_Position(mount_offset, speed, 0.5)

    def path_from_MD3(self):
        mount_offset = copy.deepcopy(Var_LSCAT.MX_Pin_Sample_Position)
        mount_offset[2] = 0.5
        speed = 0.1
        self.robot.Move_to_Position(mount_offset, speed, speed)
        speed = 2
        self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, speed)

    def mount_pin(self):

        self.log("Checking Pin Mount Status..")

        if epics.caget(self.pvs['Sample Is Mounted']) == 1:
            self.log("Sample is already mounted")
            return

        print("Mounting Sample..")

        epics.caput(self.pvs['Transfer Mode'], 2)
        starttime = time.time

        while time.time() - starttime < 10:
            if epics.caget([self.pvs['Use Sample Changer']]):
                self.log("MD3 in correct position, mounting sample.")
                break
            time.sleep(1)

        else:
            self.log("TIMEOUT: MD3 response took too long to respond")
            return
            
        self.mount_move(self.selected_pin)
        self.pin_to_dismount = self.selected_pin

    def mount_move(self, pin_to_mount):
        self.log(f"Moving robot to {self.selected_pin_name}")
        speed = 0.75

        #Copy new position for height offset as needed
        pin_offset_pos = copy.deepcopy(pin_to_mount)
        pin_offset_pos[2] = 0.25
        
        self.robot.MXGripper('off')
        self.robot.Move_to_Position(pin_offset_pos, speed, speed)
        self.robot.Move_to_Position(pin_to_mount, speed, speed)
        time.sleep(0.5)
        self.robot.MXGripper('on')
        time.sleep(0.5)
        self.robot.Move_to_Position(pin_offset_pos,speed, speed)
        self.path_to_MD3()

        speed = 0.05
        self.robot.Move_to_Position(Var_LSCAT.MX_Pin_Sample_Position, speed, speed)
        time.sleep(0.5)
        self.robot.MXGripper('off')
        time.sleep(0.5)
        speed = 2
        self.path_from_MD3()

        self.robot.Move_to_Position(pin_offset_pos, speed, speed)
        self.log("Mount Complete.")

    def dismount_pin(self):

        self.log("Checking Pin Mount Status..")
        if epics.caget(self.pvs['Sample Is Mounted']) == 0:
            self.log("No sample mounted!")
            return
        
        epics.caput(self.pvs['Transfer Mode'], 2)
        starttime = time.time

        while time.time() - starttime < 10:
            if epics.caget([self.pvs['Use Sample Changer']]):
                self.log("MD3 in correct position, dismounting sample.")
                break
            time.sleep(1)

        else:
            self.log("TIMEOUT: MD3 response took too long to respond")
            return
        
        print("Disounting Sample..")
        self.dismount_move(self.pin_to_dismount)

    def dismount_move(self, pin_to_dismount):
        speed = 2

        #Copy new position for height offset as needed
        pin_offset_pos = copy.deepcopy(pin_to_dismount)

        #Maintain safe height before move
        pin_offset_pos[2] = 0.25
        self.robot.MXGripper('off')
        self.path_to_MD3()

        speed = 0.05
        self.robot.Move_to_Position(Var_LSCAT.MX_Pin_Sample_Position, speed, speed)
        time.sleep(0.05)
        self.robot.MXGripper('on')
        time.sleep(0.5)
        self.path_from_MD3()

        speed = 0.75
        self.robot.Move_to_Position(pin_offset_pos, speed, speed)
        self.robot.Move_to_Position(self.pin_to_dismount, speed, speed)
        time.sleep(0.5)
        self.robot.MXGripper('off')
        time.sleep(0.5)
        self.robot.Move_to_Position(pin_offset_pos, speed, speed)

        print("Dismount Complete.")

    def exchange_pin(self):

        self.dismount_move(self.pin_to_dismount)
        self.mount_move(self.selected_pin)
        self.pin_to_dismount = self.selected_pin

    def go_to_wait(self):
        self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, 0.5, 0.5)

    def quit(self):
        self.robot.Disconnect()
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
