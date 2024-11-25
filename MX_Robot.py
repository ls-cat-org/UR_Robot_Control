import sys, copy, time, json, epics, os
os.environ['EPICS_CA_ADDR_LIST'] = '164.54.61.137'
import DataFiles.Var_LSCAT as Var_LSCAT
from LS_Robot_Classes import Robot_Control

def load_pvs():
    filename = os.path.join("DataFiles", "PV_config.json")
    with open(filename, 'r') as file:
        pvs = json.load(file)
    return {name: epics.PV(address) for name, address in pvs.items()}

class MX_Robot:
    def __init__(self):      
        super().__init__()  
        self.robot = Robot_Control(Var_LSCAT.RoIp)
        self.pvs = load_pvs()

        file_path = os.path.join("DataFiles", "Puck_Data.json")
        with open(file_path, "r") as file:
            self.puck_data = json.load(file)

    def get_coords(self, pv_name):
        # Read the specified PV
        print("Getting XYZ Coordinates")
        pv = self.pvs.get(pv_name)
        print(pv)
        max_retries = 3

        for attempt in range(max_retries):
            selected_pin = pv.get()
            
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
        #mount_offset = copy.deepcopy(Var_LSCAT.MX_Pin_Sample_Position)
        #mount_offset[2] = 0.5
        speed = 2
        self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
        self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, 0.5)

    def path_from_MD3(self):

        speed = 0.1
        self.robot.Move_to_Position(Var_LSCAT.MD3_Approach, speed, speed)
        speed = 2
        self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, speed)

    def mount_pin(self):

        print("Checking Pin Mount Status..")
        sample_loaded_pv = self.pvs.get('Sample Mounted')
        print(sample_loaded_pv)

        if sample_loaded_pv.get() == 1:
            print("ERROR: Sample is already mounted")
            return

        print("No Sample Mounted.")
        print("Mounting Sample..")

        time.sleep(1)
        position = self.get_coords('Sample To Mount')
        
        #print(f"Mounting sample from {selected_pin} from position {position}")

        #epics.caput('MD3:CurrentPhase', 3)
        self.pvs['Set Phase (Mount Mode)'].put(3)
        time.sleep(3)
        starttime = time.time()
        MD3_state = self.pvs.get('MD3 State')

        while time.time() - starttime < 10:
            if MD3_state.get() == 4:
                print("MD3 in correct position, mounting sample.")
                break
            time.sleep(1)
            print("Waiting on MD3 to move to safe position.")

        else:
            print("TIMEOUT: MD3 response took too long to respond")
            return
            
        self.mount_move(position)
        set_pin = self.pvs['Sample To Mount'].get()
        print(f"Sample to set: {set_pin}")
        time.sleep(2)
        self.pvs['Current Sample'].put(set_pin)
        print(f'Sample Mounted.  UR5:CurrentSample updated.')

    def mount_move(self, pin_to_mount):
        speed = 0.75

        #Copy new position for height offset as needed
        pin_offset_pos = copy.deepcopy(pin_to_mount)
        pin_offset_pos[2] = 0.25

        try:
            self.robot.MXGripper('off')
            self.robot.Move_to_Position(pin_offset_pos, speed, speed)
            self.robot.Move_to_Position(pin_to_mount, speed, speed)
            time.sleep(0.5)
            self.robot.MXGripper('on')
            time.sleep(0.5)
            self.robot.Move_to_Position(pin_offset_pos,speed, speed)
            #self.path_to_MD3()
            speed = 2
            self.robot.Move_to_Position(Var_LSCAT.Wait_Pos,speed, speed)
            self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
            self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, 0.5)
            speed = 0.75

        except Exception as e:
            print(f"Idk man the vibes were off.. {e}")
            return

        starttime = time.time()
        Cryo_Status = self.pvs.get('Cryo Status')
        self.Cryo_PV = epics.PV(f"{Cryo_Status}")
        self.Cryo_PV.put(1)

        try:
            while time.time() - starttime < 4:
                if self.Cryo_PV.get() == 0:
                    print("CRYO in correct position, mounting sample.")
                    time.sleep(1)
                    self.robot.Move_to_Position(Var_LSCAT.MD3_Approach, speed, speed)
                    speed = 0.05
                    self.robot.Move_to_Position(Var_LSCAT.MD3_Sample_Position, speed, speed)
                    time.sleep(0.5)
                    self.robot.MXGripper('off')
                    time.sleep(0.5)

                    speed = 0.1
                    self.robot.Move_to_Position(Var_LSCAT.MD3_Approach, speed, speed)
                    self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, speed)
                    Cryo_Status.put(1)

                    speed = 2
                    self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, speed)
                    self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                    print("Mount Complete.")
                    break

                time.sleep(0.5)
                print("Waiting on Cryo to safe position.")

            else:
                print("TIMEOUT: CRYO response took too long, putting sample back")
                self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, speed)
                self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, speed)
                self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                self.robot.Move_to_Position(self.pin_to_dismount, speed, speed)
                time.sleep(0.5)
                self.robot.MXGripper('off')
                time.sleep(0.5)
                self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                return
        
        except Exception as e:
 
            print(f"Idk man the vibes were off.. {e}")


    def dismount_pin(self):

        print("Checking Pin Mount Status..")
        if self.pvs["Sample Is Mounted"].get() == 0:
            print("No sample mounted!")
            return
        
        selected_pin = self.pvs['Current Sample'].get()
        position = self.get_coords(selected_pin)
        
        self.pvs['Current Phase (Mount Mode)'].put(3)
        starttime = time.time()

        while time.time() - starttime < 10:
            if self.pvs['MD3 State'].get() == 4:
                print("MD3 in correct position, dismounting sample.")
                break
            time.sleep(1)

        else:
            print("TIMEOUT: MD3 response took too long to respond")
            return
        
        print("Disounting Sample..")
        self.dismount_move(position)
        self.pvs['UR5:CurrentSample'].put('None,0')
        

    def dismount_move(self, pin_to_dismount):
        speed = 2

        #Copy new position for height offset as needed
        pin_offset_pos = copy.deepcopy(pin_to_dismount)
        pin_offset_pos[2] = 0.25


        #Try intital move to MD3 prior to CRYO move
        try:
            self.robot.MXGripper('off')
            speed = 2
            self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, 0.5)
            self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
            self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, 0.5)

        except Exception as e:
            print(f"Initial Movement failed: {e}")
            return
        
        #Set Up CRYO PV and call for retraction
        self.Cryo_PV.put(1)
        starttime = time.time()


        #Check CRYO Retracted, then mount sample
        try:
            while time.time() - starttime < 5:
                if self.Cryo_PV.get() == 0:

                    print("CRYO Retracted, continuing dismount...")


                    self.robot.Move_to_Position(Var_LSCAT.MD3_Approach, speed, speed)
                    speed = 0.05
                    self.robot.Move_to_Position(Var_LSCAT.MD3_Sample_Position, speed, speed)
                    time.sleep(0.05)
                    self.robot.MXGripper('on')
                    time.sleep(0.5)
                    #self.path_from_MD3()


                    speed = 0.75
                    self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, speed)
                    self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, speed)
                    self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                    self.robot.Move_to_Position(self.pin_to_dismount, speed, speed)
                    time.sleep(0.5)
                    self.robot.MXGripper('off')
                    time.sleep(0.5)
                    self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                    self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, speed)
                    print("Dismount Complete.")
                print("Waiting for CRYO Retract")
                time.sleep(0.5)

            #If CRYO times out, move to safe position
            else:
                print(f"Error occured during dismount process:  {e}")
                self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
                self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, 0.5)

        #If dismount fails, move to safe location
        except Exception as e:
            print(f"Error occured during dismount process:  {e}")
            self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
            self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, 0.5)
            return

    def exchange_pin(self):
        self.dismount_pin()
        time.sleep(1)
        self.mount_pin()

    def go_to_wait(self):
        self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, 0.5, 0.5)

    

