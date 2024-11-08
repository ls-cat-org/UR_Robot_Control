import sys, copy, time, datetime, math
import numpy as np
import rtde_control, rtde_receive
from rtde_io import RTDEIOInterface as RTDEIO
import pygame
import DataFIles.Var_LSCAT as Var_LSCAT
from Robotiq_Gripper.robotiq_gripper_control import RobotiqGripper

class Robot_Control:
    def __init__(self, Robot_IP):

        self.Robot_IP = Robot_IP
        self.rtde_c = rtde_control.RTDEControlInterface(Robot_IP)
        self.rtde_r = rtde_receive.RTDEReceiveInterface(Robot_IP)
        self.rtde_io = RTDEIO(Robot_IP)
        self.gripper = RobotiqGripper(self.rtde_c)
        self.ur_freq = 1/500

    def Get_Position(self):
        self.rtde_c.speedStop()
        Current_TCP = self.rtde_r.getActualTCPPose()      #Get Cartesian Coords
        Current_JOINT = self.rtde_r.getActualQ()          #Get Joint Positions
        current_time = datetime.datetime.now()
        timestamp_string = current_time.strftime("%H%M%S")
        TCP = [round(coord, 3) for coord in Current_TCP]
        JOINT = [round(coord, 3) for coord in Current_JOINT]
        new_TCP = f"Controller_TCP_{timestamp_string}"
        new_JOINT = f"Controller_JOINT_{timestamp_string}"

        with open("Var_LSCAT.py", "a") as file:                       #
            file.write(f"{new_TCP} = {TCP}\n")
            file.write(f"{new_JOINT} = {JOINT}\n")

        return TCP, JOINT

    def Move_to_Position(self, Requested_Position, speed, accel):
        self.rtde_c.speedStop()
        self.rtde_c.moveL(Requested_Position, speed, accel)

    def Jog_TCP(self, vector, accel):
        speed_vector = vector
        ur_sync = self.rtde_c.initPeriod()
        self.rtde_c.speedL(speed_vector, accel, self.ur_freq)
        self.rtde_c.waitPeriod(ur_sync)

    def Rotate_Jog_TCP(self, vector, rotational_accel):
        speed_vector = vector
        ur_sync = self.rtde_c.initPeriod()
        self.rtde_c.speedL(speed_vector, rotational_accel, self.ur_freq)
        self.rtde_c.waitPeriod(ur_sync)

    def Stop_Jog(self):
        self.rtde_c.speedStop()

    def Activate_Gripper(self):
        self.gripper.set_force(50)  # from 0 to 100 %
        self.gripper.set_speed(100)  # from 0 to 100 %
        self.gripper.activate()

    def Close_Gripper(self):
        self.gripper.set_force(50)  # from 0 to 100 %
        self.gripper.set_speed(100)  # from 0 to 100 %
        self.gripper.close()

    def Open_Gripper(self):
        self.gripper.set_force(50)  # from 0 to 100 %
        self.gripper.set_speed(100)  # from 0 to 100 %
        self.gripper.open()

    def Move_Gripper(self, finger_distance):
        self.gripper.set_force(50)  # from 0 to 100 %
        self.gripper.set_speed(100)  # from 0 to 100 %
        self.gripper.move(finger_distance)

    def Disconnect(self):
        self.rtde_c.speedStop()
        self.rtde_c.stopScript()
        self.rtde_c.disconnect()
        self.rtde_r.disconnect()

    def Screwdrive(self, move_direction, screw_depth, thread_pitch):
        vertical_speed = 0.0005
        direction = move_direction
        depth = screw_depth
        pitch = thread_pitch
        run_time = depth * 2
        screw_vector = [0, 0, 0, 0, 0, 0]

        if direction == 'down':
            rotational_speed = ((vertical_speed*1000) / thread_pitch) * (2 * math.pi)
            screw_vector[2] = -vertical_speed
            screw_vector[5] = -rotational_speed
            start_time = time.time()

            while (time.time() - start_time) < run_time:
                ur_sync = self.rtde_c.initPeriod()
                self.rtde_c.speedL(screw_vector, 10, self.ur_freq)
                self.rtde_c.waitPeriod(ur_sync)

            self.rtde_c.speedStop()

        elif direction == 'up':
            rotational_speed = ((vertical_speed*1000) / thread_pitch) * (2 * math.pi)
            screw_vector[2] = vertical_speed
            screw_vector[5] = rotational_speed
            start_time = time.time()

            while (time.time() - start_time) < (run_time + 1):
                ur_sync = self.rtde_c.initPeriod()
                self.rtde_c.speedL(screw_vector, 10, self.ur_freq)
                self.rtde_c.waitPeriod(ur_sync)

            self.rtde_c.speedStop()

        else:
            print("Invalid Argument!")

    def MXGripper(self, on_off):

        lower_on_off = on_off.lower()

        if lower_on_off == "on":
            self.rtde_io.setStandardDigitalOut(0, True)

        elif lower_on_off == "off":
            self.rtde_io.setStandardDigitalOut(0, False)

        else:
            print("Hell noo that ain't right!")

    def Gripper_Swap(self, on_off):
        
        speed = 0.5
        slow = 0.1

        command = on_off.lower()

        if command == "mount":
            self.rtde_io.setStandardDigitalOut(1, False)
            Gripper_Approach = copy.deepcopy(Var_LSCAT.Gripper_Mount)
            Gripper_Approach[2] += 0.05

            Gripper_Detach = copy.deepcopy(Var_LSCAT.Gripper_Mount)
            Gripper_Detach[0] -= 0.06

            Gripper_Free = copy.deepcopy(Var_LSCAT.Gripper_Mount)
            Gripper_Free[0] -= 0.06
            Gripper_Free[2] += 0.325
            
            print(Gripper_Approach)
            self.rtde_c.moveL(Gripper_Approach, speed, speed)
            #time.sleep(0.5)
            print(Var_LSCAT.Gripper_Mount)
            self.rtde_c.moveL(Var_LSCAT.Gripper_Mount, slow, slow)
            time.sleep(0.5)
            

            print(Gripper_Detach)
            self.rtde_c.moveL(Gripper_Detach, slow, slow)
            time.sleep(0.5)
            self.rtde_io.setStandardDigitalOut(1, True)
            time.sleep(0.5)
            self.rtde_io.setStandardDigitalOut(0, True)
            time.sleep(0.5)
            self.rtde_io.setStandardDigitalOut(0, False)
            self.rtde_c.moveL(Gripper_Free, speed, speed)
            self.rtde_c.moveL(Var_LSCAT.Wait_Pos, speed, speed)



        elif command == "dismount":
            self.rtde_io.setStandardDigitalOut(1, False)
            Gripper_Attach = copy.deepcopy(Var_LSCAT.Gripper_Mount)
            Gripper_Attach[0] -= 0.06

            Gripper_Approach = copy.deepcopy(Var_LSCAT.Gripper_Mount)
            Gripper_Approach[0] -= 0.06
            Gripper_Approach[2] += 0.325

            Gripper_Free = copy.deepcopy(Var_LSCAT.Gripper_Mount)
            Gripper_Free[2] += 0.05

            self.rtde_c.moveL(Gripper_Approach, speed, speed)
            #time.sleep(0.5)
            self.rtde_c.moveL(Gripper_Attach, speed, speed)
            #time.sleep(0.5)
            self.rtde_c.moveL(Var_LSCAT.Gripper_Mount, slow, slow)
            time.sleep(0.5)
            self.rtde_c.moveL(Gripper_Free, slow, slow)
            self.rtde_c.moveL(Var_LSCAT.Wait_Pos, speed, speed)

        else:
            print("Hell noo that ain't right!")

# class Joystick_Robot_Controller:
#     def __init__(self, Robot_IP):
#         pygame.init()

#         self.IP = Robot_IP
#         self.robot = Robot_Control(self.IP)

#         self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
#         pygame.display.set_caption('UR3e Gamepad Control')

#         self.motion = [0, 0]
#         self.speed_vector = [0] * 6

#         screen = pygame.display.set_mode((500, 500), 0, 32)
#         screen.fill((0, 0, 0))

#     def handle_axis_motion(self, event, speed, accel):
#         if event.axis < 2:
#             if event.axis == 0:
#                 self.motion[0] = event.value
#                 self.speed_vector[0] = -event.value * speed

#             if event.axis == 1:
#                 self.motion[1] = event.value
#                 self.speed_vector[1] = event.value * speed

#             if abs(self.speed_vector[event.axis]) < 0.01:
#                 self.speed_vector[event.axis] = 0

#             self.robot.Jog_TCP(self.speed_vector, accel)

#         elif 2 <= event.axis <= 3:
#             if event.axis == 2:
#                 rot_accel = 25
#                 self.speed_vector[5] = -event.value

#                 if abs(self.speed_vector[5]) < 0.03:
#                     self.speed_vector[5] = 0

#                 self.robot.Rotate_Jog_TCP(self.speed_vector, rot_accel)

#             if event.axis == 3:
#                 self.speed_vector[2] = -event.value * speed

#                 if abs(self.speed_vector[2]) < 0.02:
#                     self.speed_vector[2] = 0

#                 self.robot.Jog_TCP(self.speed_vector, accel)

#         elif event.axis == 5:
#             self.robot.MX_Gripper('on')

#         elif event.axis == 4:
#             self.robot.MX_Gripper('off')


#     def handle_button_press(self, event, speed):
#         if event.button == 0:
#             self.robot.Get_Position()
#             print("A Button Pressed")

#         elif event.button == 3:
#             print("Y Button Pressed")
#             self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, speed, speed)
#             print("Robot Moved Home")

#         elif event.button == 7:
#             self.handle_quit_event()
#             print("Start Button Pressed")

#         elif event.button == 6:
#             self.robot.Activate_Gripper()
#             print("Menu Button Pressed")


#     def handle_joy_device_events(self, event):
#         if event.type == pygame.JOYDEVICEADDED:
#             self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
#         elif event.type == pygame.JOYDEVICEREMOVED:
#             self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

#     def handle_quit_event(self):
#         print("Closing Gamepad Control...")
#         pygame.quit()
#         self.robot.Disconnect()
#         sys.exit()

#     def run(self, speed, accel):
#         running = True
#         joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

#         print("Connected")

#         while running:
#             for event in pygame.event.get():
#                 if event.type == pygame.JOYAXISMOTION:
#                     self.handle_axis_motion(event, speed, accel)
#                 elif event.type == pygame.JOYBUTTONDOWN:
#                     self.handle_button_press(event, speed)
#                 elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
#                     self.handle_joy_device_events(event)
#                 elif event.type == pygame.QUIT:
#                     self.handle_quit_event()

# class Joystick_Control_PyQT:
#     def __init__(self, Robot_IP):
#         pygame.init()
#         self.IP = Robot_IP
#         self.robot = Robot_Control(self.IP)
#         self.running = False
#         self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
#         self.motion = [0, 0]
#         self.speed_vector = [0] * 6

#     def handle_axis_motion(self, event, speed, accel):
#         if event.axis < 2:
#             if event.axis == 0:
#                 self.motion[0] = event.value
#                 self.speed_vector[0] = -event.value * speed

#             if event.axis == 1:
#                 self.motion[1] = event.value
#                 self.speed_vector[1] = event.value * speed

#             if abs(self.speed_vector[event.axis]) < 0.01:
#                 self.speed_vector[event.axis] = 0

#             self.robot.Jog_TCP(self.speed_vector, accel)

#         elif 2 <= event.axis <= 3:
#             if event.axis == 2:
#                 rot_accel = 20
#                 self.speed_vector[5] = -event.value
#                 if abs(self.speed_vector[5]) < 0.03:
#                     self.speed_vector[5] = 0
#                 self.robot.Rotate_Jog_TCP(self.speed_vector, rot_accel)

#             if event.axis == 3:
#                 self.speed_vector[2] = -event.value * speed
#                 if abs(self.speed_vector[2]) < 0.02:
#                     self.speed_vector[2] = 0
#                 self.robot.Jog_TCP(self.speed_vector, accel)

#         elif event.axis == 5:
#             self.robot.MX_Gripper('on')

#         elif event.axis == 4:
#             self.robot.MX_Gripper('off')

#     def handle_button_press(self, event, speed):
#         if event.button == 0:
#             self.robot.Get_Position()
#             print("A Button Pressed.")

#         elif event.button == 3:
#             print("Y Button Pressed.")
#             self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, speed, speed)
#             time.sleep(2)
#             print("Robot Moved Home.")

#         elif event.button == 7:
#             print("Start Button Pressed.")
#             self.handle_quit_event()

#         elif event.button == 6:
#             self.robot.Activate_Gripper()
#             print("Menu Button Pressed.")

#     def handle_joy_device_events(self, event):
#         if event.type == pygame.JOYDEVICEADDED:
#             self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

#         elif event.type == pygame.JOYDEVICEREMOVED:
#             self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

#     def handle_quit_event(self):
#         print("Stopping Gamepad Control...")
#         self.stop()

#     def run(self, speed, accel):
#         self.running = True
#         pygame.event.clear() #Clear stored states, this is important!
#         joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
#         time.sleep(2)
#         print("Controller connected.")

#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == pygame.JOYAXISMOTION:
#                     self.handle_axis_motion(event, speed, accel)

#                 elif event.type == pygame.JOYBUTTONDOWN:
#                     self.handle_button_press(event, speed)

#                 elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
#                     self.handle_joy_device_events(event)

#                 elif event.type == pygame.QUIT:
#                     self.handle_quit_event()
#                     self.running = False

#     def stop(self):
#         self.running = False
#         self.robot.Disconnect()
#         time.sleep(2)
#         print("Controller disconnected.")

# # class Joystick_Control_GRIPTEST:
# #     def __init__(self, Robot_IP):
# #         pygame.init()
# #         self.IP = Robot_IP
# #         self.robot = Robot_Control(self.IP)
# #         self.running = False
# #         self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
# #         self.motion = [0, 0]
# #         self.speed_vector = [0] * 6

# #     def handle_axis_motion(self, event, speed, accel):
# #         if event.axis < 2:
# #             if event.axis == 0:
# #                 self.motion[0] = event.value
# #                 self.speed_vector[0] = -event.value * speed

# #             if event.axis == 1:
# #                 self.motion[1] = event.value
# #                 self.speed_vector[1] = event.value * speed

# #             if abs(self.speed_vector[event.axis]) < 0.01:
# #                 self.speed_vector[event.axis] = 0

# #             self.robot.Jog_TCP(self.speed_vector, accel)

# #         elif 2 <= event.axis <= 3:
# #             if event.axis == 2:
# #                 rot_accel = 25
# #                 self.speed_vector[5] = -event.value
# #                 if abs(self.speed_vector[5]) < 0.03:
# #                     self.speed_vector[5] = 0
# #                 self.robot.Rotate_Jog_TCP(self.speed_vector, rot_accel)

# #             if event.axis == 3:
# #                 self.speed_vector[2] = -event.value * speed
# #                 if abs(self.speed_vector[2]) < 0.02:
# #                     self.speed_vector[2] = 0
# #                 self.robot.Jog_TCP(self.speed_vector, accel)

# #         elif event.axis == 5:
# #             self.robot.MXGripper('on')

# #         elif event.axis == 4:
# #             self.robot.MXGripper('off')

# #     def handle_button_press(self, event, speed):
# #         if event.button == 0:
# #             self.TCP, self.JOINT = self.robot.Get_Position()
# #             print("A Button Pressed.")

# #         elif event.button == 3:
# #             print("Y Button Pressed.")
# #             self.robot.Move_to_Position(Var_LSCAT.MX_Wait_Pos, speed, speed)
# #             time.sleep(2)
# #             print("Robot Moved Home.")

# #         elif event.button == 7:
# #             print("Start Button Pressed.")
# #             self.handle_quit_event()

# #         elif event.button == 6:
# #             self.robot.Activate_Gripper()
# #             print("Menu Button Pressed.")

# #     def handle_joy_device_events(self, event):
# #         if event.type == pygame.JOYDEVICEADDED:
# #             self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

# #         elif event.type == pygame.JOYDEVICEREMOVED:
# #             self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

# #     def handle_quit_event(self):
# #         print("Stopping Gamepad Control...")
# #         self.stop()

# #     def run(self, speed, accel):
# #         self.running = True
# #         pygame.event.clear() #Clear stored states, this is important!
# #         joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
# #         time.sleep(2)
# #         print("Controller connected.")

# #         while self.running:
# #             for event in pygame.event.get():
# #                 if event.type == pygame.JOYAXISMOTION:
# #                     self.handle_axis_motion(event, speed, accel)

# #                 elif event.type == pygame.JOYBUTTONDOWN:
# #                     self.handle_button_press(event, speed)

# #                 elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
# #                     self.handle_joy_device_events(event)

# #                 elif event.type == pygame.QUIT:
# #                     self.handle_quit_event()
# #                     self.running = False

# #     def stop(self):
# #         self.running = False
# #         self.robot.Disconnect()
# #         time.sleep(2)
# #         print("Controller disconnected.")
