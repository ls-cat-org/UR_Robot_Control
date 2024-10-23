#Variables for UR3e Development

def save_position_variable(variable_name, position):
    with open("Var_LSCAT.py", "a") as file:
        file.write(f"{variable_name} = {position}\n\n")

#Robot IP
RoIp = "169.254.45.17"

location_count = 1
gripper_status = 0

#Position Variables
Wait_Pos =               [-0.443, 0.153, 0.5, 3.141, 0.0, -0.0]
Dewer_Hover =            [-0.443, 0.153, 0.5, 3.141, 0.0, -0.0]
MX_Wait_Pos =            [-0.443, 0.153, 0.5, 3.141, 0.0, -0.0]
MX_Pin_Sample_Position = [-0.246, 0.637, 0.44, 3.141, 0.0, 0.0]
Path_Near_Dewer =        [-0.334, 0.435, 0.5, 3.141, 0.0, -0.0]
Gripper_Mount =          [-0.828, -0.091, -0.077, -2.197, -2.239, 0.008]
#Path_Near_MD3 =          

#Captured Positions:


