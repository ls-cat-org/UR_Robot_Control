from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run, PvpropertyString
from caproto import ChannelType
import MX_Robot as Robot

# Assuming your UR5Robot class now takes puck and sample arguments for mount and exchange
# from ur5_robot import UR5Robot


class UR5RobotIOC(PVGroup):
    # PVs for specifying the puck and sample numbers
    SampleToMount = pvproperty(value='None,0', dtype=ChannelType.STRING, string_encoding='latin-1')
    CurrentSample = pvproperty(value='None,0', dtype=ChannelType.STRING, string_encoding='latin-1')
    MountSample = pvproperty(value=0, dtype=int, doc="Trigger mount function")
    DismountSample = pvproperty(value=0, dtype=int, doc="Trigger dismount function")
    ExchangeSample = pvproperty(value=0, dtype=int, doc="Trigger exchange function")
    GoHome = pvproperty(value=0, dtype=int, doc="Send Robot to Home Position")


    @MountSample.putter
    async def MountSample(self, instance, value):
        if value == 1:
            Robot.mount_pin()
            print("Hello you mounted")
        return 0  # Reset to 0 after call

    @DismountSample.putter
    async def DismountSample(self, instance, value):
        if value == 1:
            Robot.dismount_pin()
            print("Hello you dismounted")
        return 0

    @ExchangeSample.putter
    async def ExchangeSample(self, instance, value):
        if value == 1:
            Robot.exchange_pin()
            print("You Exchanged Samples")
        return 0
    
    @GoHome.putter
    async def ExchangeSample(self, instance, value):
        if value == 1:
            print("You Exchanged Samples")
        return 0
    

        

if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="UR5:",
        desc="UR5 Robot IOC with Puck and Sample Specification"
    )
    ioc = UR5RobotIOC(**ioc_options)
    run(ioc.pvdb, **run_options)