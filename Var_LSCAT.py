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
Gripper_Mount = [-0.820, -0.091, -0.077, -2.197, -2.233, 0.013]
#Path_Near_MD3 =          

#Captured Positions:


Path1 = [-0.408, 0.065, 0.65, 3.139, -0.139, -0.0]
Path2 = [-0.162, -0.67, 0.58, 3.14, -0.096, 0.0]
MountApproach = [-0.162, -0.738, 0.472, -3.14, 0.096, -0.0]
MountMD3 = [-0.16, -0.738, 0.441, 3.14, -0.096, -0.0]
NewDewerHover = [-0.443, 0.153, 0.499, 3.141, 0.0, -0.0]
NewMD3Approach = [-0.334, 0.435, 0.499, 3.141, 0.0, -0.0]
foo = [-0.444, 0.153, 0.496, 3.128, 0.005, 0.014]
Gripper_Mount = [-0.829, -0.091, -0.078, -2.179, -2.259, 0.001]
Gripper_Dismount = [-0.865, -0.09, -0.071, -2.171, -2.251, 0.017]
testtiboii = [-0.877, -0.089, -0.079, 2.173, 2.251, -0.019]
test = [-0.83, -0.091, -0.077, -2.197, -2.233, 0.013]
