import sys, copy, time, json, epics, os
os.environ['EPICS_CA_ADDR_LIST'] = '164.54.61.137'
import DataFiles.Var_LSCAT as Var_LSCAT
from MX_Robot_Utils import Utilities


class MX_Robot:
    def __init__(self):      
        super().__init__()
        #Initialize PVs from PV_Config.json
        filename = os.path.join("DataFiles", "PV_config.json")
        self.pvs = self.load_pvs(filename)
        self.utils = Utilities(self.pvs)

        #Load in Puck Data from Puck_Data,json
        file_path = os.path.join("DataFiles", "Puck_Data.json")
        with open(file_path, "r") as file:
            self.puck_data = json.load(file)

    def load_pvs(self, filepath):
        with open(filepath, 'r') as file:
            pvs = json.load(file)
        return {name: epics.PV(address) for name, address in pvs.items()}
    
    #Set-Up and call of Mounting Sample Function
    def mount_pin(self):

        print("Checking Pin Mount Status..")

        #Check if there is a sample mounted to avoid possible crash
        if self.pvs['Sample Mounted'].get(use_monitor=False) == 1:
            print("ERROR: Sample is already mounted")
            return

        print("No Sample Mounted.")
        print("Mounting Sample..")

        position = self.utils.get_coords('Sample To Mount')

        if position is not None:
            print(f"Position: {position}")

        else: 
            print('ERROR: get_coords returned None value. Exiting function...')
            return
        
        #Set MD3 phase to move to sample mount position and capture Sample_to_mount string
        sample_string = self.pvs['Sample To Mount'].get(use_monitor=False)
        self.pvs['Set Phase (Mount Mode)'].put(3)
        starttime = time.time()
        dots = 1

        try:
            #Wait for MD3 to move into mount state
            while time.time() - starttime < 15:
                if self.pvs['MD3 State'].get(use_monitor=False) == 4:
                    print("MD3 in correct position, mounting sample.")
                    self.utils.mount_move(position)

                    time.sleep(1)

                    print(f"Setting Current_Sample to {sample_string}")
                    sample_updated = self.pvs['Current Sample'].put(sample_string, wait=True, timeout=10)

                    if not sample_updated:
                        print("ERROR: Could not update CurrentSample PV")
                        return
                        
                    time.sleep(1)
                    print(f"Current Sample Set to: {sample_string}")
                    print(f'Sample Mounted. Movinng MD3 to Data Collection Position')
                    self.pvs['Set Phase (Mount Mode)'].put(2)
                    return

                print(f"\rWaiting on MD3 to move to safe position{'.' * dots:<3}", end="")
                dots = dots + 1 if dots < 3 else 1  # Increment dots, reset to 1 after 3
                time.sleep(0.5)

            else:
                print("TIMEOUT: MD3 response took too long to respond")
                return
                
        except Exception as e:
            print(f"Error occured during mount_pin function! {e}")


    #Set-Up and call of dismounting pin function
    def dismount_pin(self):

        print("Checking Pin Mount Status..")

        if self.pvs['Sample Mounted'].get(use_monitor=False) == 0:
            print("No sample mounted!")
            return
        
        position = self.utils.get_coords('Current Sample')
        
        self.pvs['Set Phase (Mount Mode)'].put(3)
        #Create monitor to check for MD3_State Status change before starting loop
        time.sleep(4)
        starttime = time.time()
        dots = 1

        while time.time() - starttime < 15:
            if self.pvs['MD3 State'].get() == 4:
                print("MD3 in correct position, dismounting sample.")
                self.utils.dismount_move(position)
                break

            time.sleep(0.5)

            print(f"\rWaiting on MD3 to move to safe position{'.' * dots:<3}", end="")
            dots = dots + 1 if dots < 3 else 1  # Increment dots, reset to 1 after 3
            time.sleep(0.5)

        else:
            print("TIMEOUT: MD3 response took too long to respond")
            return

    def exchange_pin(self):
        self.dismount_pin()
        time.sleep(2)
        self.mount_pin()

    def go_to_wait(self):
        self.utils.Go_Home()