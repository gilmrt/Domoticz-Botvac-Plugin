# Plugin to control Botvac Vacuum
#
# Author: gilmrt
#
"""
<plugin key="BotvacVaccum" name="Botvac Vaccum" author="gilmrt" version="1.0.0" externallink="https://github.com/gilmrt/Domoticz-Botvac-Plugin">
    <description>
        <h2>Botvac vacuum</h2><br/>
        Python plugin to control your Botvac Vacuum
    </description>
     <params>
        <param field="Mode1" label="Name" width="200px" required="true" default=""/>
        <param field="Mode2" label="Serial" width="200px" required="true" default=""/>
        <param field="Mode3" label="Secret" width="200px" required="true" default=""/>
        <param field="Mode4" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
        <param field="Mode5" label="Update interval (sec)" width="30px" required="true" default="60"/>
    </params>
</plugin>
"""
import Domoticz
from pybotvac import Robot

class BasePlugin:
    enabled = False
    iconName = 'botvac-robot-vacuum-icon'

    statusUnit = 1
    controlUnit = 2
    scheduleUnit = 3

    HeartBeatsCount = 0

    controlValues = {
        0: 'Off',
        10: 'Clean',
        20: 'Base',
        30: 'Spot',
        40: 'Pause',
        50: 'Stop'
    }

    controlNameModes = "|".join(str(value) for value in controlValues.values())

    controlOptions = {
        "LevelActions": "|||||",
        "LevelNames": controlNameModes,
        "LevelOffHidden": "true",
        "SelectorStyle": "0"
    }

    # https://developers.neatorobotics.com/api/robot-remote-protocol/request-response-formats
    actions = {
        0: 'Invalid',
        1: 'House Cleaning',
        2: 'Spot Cleaning',
        3: 'Manual Cleaning',
        4: 'Docking',
        5: 'User Menu Active',
        6: 'Suspended Cleaning',
        7: 'Updating',
        8: 'Copying Logs',
        9: 'Recovering Location',
        10: 'IEC Test',
        11: 'Map cleaning',
        12: 'Exploring map',
        13: 'Acquiring Persistent Map IDs',
        14: 'Creating & Uploading Map',
        15: 'Suspended Exploration',
        100: 'Stopped',
        101: 'Based',
        102: 'Charging'
    }

    states = {
        0: 'Invalid',
        1: 'Idle',
        2: 'Busy',
        3: 'Paused',
        4: 'Error'
    }

    categories = {
        1: 'manual',
        2: 'house',
        3: 'spot',
        4: 'map'
    }

    modes = {
        1: 'eco',
        2: 'turbo'
    }

    navigationModes = {
        1: 'normal',
        2: 'extra care',
        3: 'deep'
    }


    def __init__(self):
        return

    def onStart(self):
        if Parameters["Mode4"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()

        if iconName not in Images: 
            Domoticz.Image('icons.zip').Create()
        iconID = Images[iconName].ID

        if statusUnit not in Devices:
            Domoticz.Device(Name='Status', Unit=statusUnit, Type=17,  Switchtype=17, Image=iconID, Used=1).Create()

        if controlUnit not in Devices:
            Domoticz.Device(Name='Control', Unit=controlUnit, TypeName='Selector Switch', Image=iconID, Options=controlOptions, Used=1).Create()

        if scheduleUnit not in Devices:
            Domoticz.Device(Name='Schedule', Unit=scheduleUnit, TypeName='Switch', Image=iconID, Used=1).Create()

        Domoticz.Heartbeat(int(Parameters['Mode5']))
        Domoticz.Debug("onStart called")

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("on Message called ")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("on Message called ")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        DEVICE_NAME = Parameters["Mode1"]
        DEVICE_SERIAL = Parameters["Mode2"]
        API_SECRET = Parameters["Mode3"]
        robot = Robot(DEVICE_SERIAL, API_SECRET, DEVICE_NAME)
        response = robot.state
        state = response['state']
        action = response['action']
        category = response['cleaning']['category']
        
        if statusUnit not in Devices:
            Domoticz.Error('Status device is required')
            return

        if statusUnit == Unit:
            if 'On' == Command and isOFF:
                robot.start_cleaning()
                if category == 1: #manual
                    Devices[statusUnit].Update(1, actions.get(3))
                elif category == 2: #house
                    Devices[statusUnit].Update(1, actions.get(1))
                elif category == 3: #spot
                    Devices[statusUnit].Update(1, actions.get(2))
                elif category == 4: #map
                    Devices[statusUnit].Update(1, actions.get(11))
            elif 'Off' == Command and isON:
                robot.send_to_base()
                Devices[statusUnit].Update(0, actions.get(4))

        if controlUnit == Unit:
            if Level == 10 and isOFF: # Clean
                if state == 1: #Idle
                    robot.start_cleaning()
                elif state == 3: #Pause
                    robot.resume_cleaning()
                Devices[statusUnit].Update(1, actions.get(action))
            elif Level == 20 and isON: # Base
                robot.send_to_base()
                Devices[statusUnit].Update(0, actions.get(action))
            elif Level == 30 and isOFF: # Spot
                robot.start_spot_cleaning()
                Devices[statusUnit].Update(1, actions.get(action))
            elif Level == 40 and isON: # Pause
                robot.pause_cleaning()
                Devices[statusUnit].Update(0, actions.get(action))
            elif Level == 50 and isON: # Stop
                robot.stop_cleaning()
                Devices[statusUnit].Update(0, actions.get(action))

        if scheduleUnit == Unit:
            if Command == 'On' :
                robot.enable_schedule()
                Devices[scheduleUnit].Update(1,'')
            elif Command == 'Off' :
                robot.disable_schedule()
                Devices[scheduleUnit].Update(0,'')
        
        
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        HeartBeatsCount = HeartBeatsCount + 1
        # API call every 6 heartbeats (~1min)
        if HeartBeatsCount >= 6:
            HeartBeatsCount = 0
            botvacGetValues()

    def botvacGetValues(self):
        DEVICE_NAME = Parameters["Mode1"]
        DEVICE_SERIAL = Parameters["Mode2"]
        API_SECRET = Parameters["Mode3"]
        robot = Robot(DEVICE_SERIAL, API_SECRET, DEVICE_NAME)
        response = robot.state

        isCharging = response['details']['isCharging']
        isDocked = response['details']['isDocked']
        isScheduleEnabled = response['details']['isScheduleEnabled']
        charge = response['details']['charge']
        state = response['state']
        action = response['action']

        device_on = 1 if state == 2 else 0

        if state == 1: # Idle
            if isDocked:
                statusValue = actions.get(102) if isCharging else actions.get(101) #Charging or Base
            else:
                statusValue = actions.get(100) #Stopped
            controlValue = controlValues.get(20) if isDocked else controlValues.get(50) #Base or Stop

        elif state == 2: #Busy
            statusValue = actions.get(action)
            if action in [1, 3, 11]: #House cleaning, Manual cleaning or Map cleaning
                controlValue = controlValues.get(10) #Clean
            elif action == 2: #Spot
                controlValue = controlValues.get(30) #Spot

        elif state in [3, 4]: #Pause or Error
            statusValue = states.get(state)
            controlValue = controlValues.get(40) if states.get(state) == 3 else controlValues.get(50) #Pause or Stop

        Devices[statusUnit].Update(device_on, str(statusValue))
        Devices[controlUnit].Update(1, str(controlValue))
        Devices[scheduleUnit].Update(isScheduleEnabled, '')


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


### Generic helper functions
@property
def isON(self):
    return Devices[statusUnit].nValue == 1

@property
def isOFF(self):
    return Devices[statusUnit].nValue == 0

def UpdateDevice(Unit, nValue, sValue, BatteryLevel=255):
    if Unit not in Devices: return

    if Devices[Unit].nValue != nValue\
        or Devices[Unit].sValue != sValue\
        or Devices[Unit].BatteryLevel != BatteryLevel:

        Devices[Unit].Update(nValue=nValue, sValue=str(sValue), BatteryLevel=BatteryLevel)

        Domoticz.Debug("Update %s: nValue %s - sValue %s - BatteryLevel %s" % (
            Devices[Unit].Name,
            nValue,
            sValue,
            BatteryLevel
        ))
    return

    
def UpdateIcon(Unit, iconID):
    if Unit not in Devices: return
    d = Devices[Unit]
    if d.Image != iconID: d.Update(d.nValue, d.sValue, Image=iconID)

def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return