import sys, copy, time, json, epics, os
os.environ['EPICS_CA_ADDR_LIST'] = '164.54.61.137'
import DataFIles.Var_LSCAT as Var_LSCAT
from LS_Robot_Classes import Robot_Control

class MX_Robot:
    def __init__(self):      
        super().__init__()  
        self.robot = Robot_Control(Var_LSCAT.RoIp)
        self.pvs = {}


        file_path = os.path.join("DataFiles", "Puck_Data.json")
        with open(file_path, "r") as file:
            self.puck_data = json.load(file)

    def load_pvs(self):
        filename = os.path.join("DataFiles", "MD3_PV_config.json")
        with open(filename, 'r') as file:
            self.pvs = json.load(filename)

    def get_coords(self, pv_name):
        # Read the specified PV
        print("Getting XYZ Coordinates")
        pv = pv_name
        print(pv)
        max_retries = 5

        for attempt in range(max_retries):
            selected_pin = epics.caget(pv)
            
            if selected_pin is not None:
                break  # Exit the loop if we got a value
            else:
                print(f"Attempt {attempt + 1} of {max_retries}: PV {pv_name} returned None. Retrying...")

        else:
            print(f"Error: PV {pv_name} returned None after {max_retries} attempts.")
            return None 
        # Try to parse the puck and pin information from the PV value
        try:
            puck, pin_str = selected_pin.split(",")
            pin = int(pin_str)  # Convert pin number to integer
        except (ValueError, AttributeError) as e:
            print(f"Error parsing {pv_name} value '{selected_pin}': {e}")
            return None  # Return None or appropriate error value
        
        # Position data retrieval logic directly included
        try:
            # Read the JSON file (or however it's stored)
            file_path = os.path.join("DataFiles", "Puck_Data.json")
            with open(file_path, 'r') as f:
                position_data = json.load(f)

            # Loop through the JSON list to find the matching puck
            for puck_data in position_data:
                if puck_data["Puck Name"] == puck:
                    # Look for the pin in the "Pin Positions" dictionary
                    pin_key = f"Pin_{pin}"
                    if pin_key in puck_data["Pin Positions"]:
                        position = puck_data["Pin Positions"][pin_key]
                        return position  # Return the position when found

            # If we reach here, it means no matching puck or pin was found
            print(f"Position data not found for puck {puck}, pin {pin}.")
            return None  # Return None if position not found
        except FileNotFoundError:
            print("Error: Position data JSON file not found.")
            return None
        except json.JSONDecodeError:
            print("Error: Failed to decode the position data JSON file.")
            return None

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

        print("Checking Pin Mount Status..")

        if epics.caget('MD3:SampleIsLoaded') == 1:
            print("ERROR: Sample is already mounted")
            return

        print("No Sample Mounted.")
        print("Mounting Sample..")

        time.sleep(1)
        position = self.get_coords('UR5:SampleToMount')
        
        #print(f"Mounting sample from {selected_pin} from position {position}")

        epics.caput('MD3:CurrentPhase', 3)
        time.sleep(3)
        starttime = time.time()

        while time.time() - starttime < 10:
            if epics.caget("MD3:State") == 4:
                print("MD3 in correct position, mounting sample.")
                break
            time.sleep(1)
            print("Waiting on MD3 to move to safe position.")

        else:
            print("TIMEOUT: MD3 response took too long to respond")
            return
            
        self.mount_move(position)
        set_pin = epics.caget('UR5:SampleToMount')
        print(set_pin)
        time.sleep(2)
        epics.caput('UR5:CurrentSample', set_pin)
        print(f'Sample Mounted.  UR5:CurrentSample updated.')

    def mount_move(self, pin_to_mount):
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
        print("Mount Complete.")

    def dismount_pin(self):

        print("Checking Pin Mount Status..")
        if epics.caget(self.pvs['Sample Is Mounted']) == 0:
            print("No sample mounted!")
            return
        
        selected_pin = epics.caget('UR5:CurrentSample')
        position = self.get_coords('UR5:CurrentSample')
        
        epics.caput(epics.caput('MD3:CurrentPhase', 3))
        starttime = time.time()

        while time.time() - starttime < 10:
            if epics.caget("MD3:State") == 4:
                print("MD3 in correct position, dismounting sample.")
                break
            time.sleep(1)

        else:
            print("TIMEOUT: MD3 response took too long to respond")
            return
        
        print("Disounting Sample..")
        self.dismount_move(position)
        epics.caput('UR5:CurrentSample', 'None,0')

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
        
        self.dismount_pin()
        self.mount_pin()
        #self.pin_to_dismount = self.selected_pin

    def go_to_wait(self):
        self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, 0.5, 0.5)

    

