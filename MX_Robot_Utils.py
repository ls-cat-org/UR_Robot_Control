import sys, copy, time, json, epics, os
import DataFiles.Var_LSCAT as Var_LSCAT
from LS_Robot_Classes import Robot_Control

class Utilities:
    def __init__(self, pvs):

        self.robot = Robot_Control(Var_LSCAT.RoIp)
        self.pvs = pvs


    def get_coords(self, pv_name):
        print("Getting XYZ Coordinates")
        max_retries = 4

        for attempt in range(max_retries):
            selected_pin = self.pvs[pv_name].get(timeout=5)

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
        self.pvs['Cryo Status'].put(1)
        starttime = time.time()


        #Check CRYO Retracted, then mount sample
        try:
            while time.time() - starttime < 5:
                if self.pvs['Cryo Status'].get(use_monitor=False) == 1:

                    print("CRYO Retracted! Continuing dismount...")

                    self.robot.Move_to_Position(Var_LSCAT.MD3_Approach, speed, speed)
                    speed = 0.05
                    self.robot.Move_to_Position(Var_LSCAT.MD3_Sample_Position, speed, speed)
                    time.sleep(0.05)
                    self.robot.MXGripper('on')
                    time.sleep(0.5)

                    speed = 0.1
                    self.robot.Move_to_Position(Var_LSCAT.MD3_Approach, speed, speed)
                    self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, speed)
                    self.pvs['Cryo Status'].put(0)

                    #self.path_from_MD3()
                    
                    speed = 0.75
                    self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, speed)
                    self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, speed)
                    self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                    self.robot.Move_to_Position(pin_to_dismount, speed, speed)
                    time.sleep(0.5)
                    self.robot.MXGripper('off')
                    time.sleep(0.5)
                    self.robot.Move_to_Position(pin_offset_pos, speed, speed)
                    print("Dismount Complete.")
                    break

                print("Waiting for CRYO Retract")
                time.sleep(0.5)

            #If CRYO times out, move to safe position
            else:
                print(f"Error occured during dismount process:  {e}")
                self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
                self.robot.Move_to_Position(Var_LSCAT.Wait_Pos, speed, 0.5)
                return

        #If dismount fails, move to safe location
        except Exception as e:
            print(f"Error occured during dismount process:  {e}")
            return

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
            speed = 2
            self.robot.Move_to_Position(Var_LSCAT.Wait_Pos,speed, speed)
            self.robot.Move_to_Position(Var_LSCAT.Path_Near_Dewer, speed, 0.5)
            self.robot.Move_to_Position(Var_LSCAT.Wait_for_Cryo, speed, 0.5)
            speed = 0.75

        except Exception as e:
            print(f"Error During Initial Robot Movement: {e}")
            return

        self.pvs['Cryo Status'].put(1)
        starttime = time.time()
        #Cryo_Status = self.pvs.get('Cryo Status')
        
        try:
            while time.time() - starttime < 4:
                if self.pvs['Cryo Status'].get(use_monitor=False) == 1:
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
                    self.pvs['Cryo Status'].put(0)

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
            print(f"Sample Could not be mounted! {e}")

    def Go_Home(self):
        self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, 0.5, 0.5)