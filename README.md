# Domoticz-Botvac-Plugin
 Domoticz Plugin for Botvac (Neato) Vacuum
 
 *This plugin uses the [pybotvac](https://github.com/stianaske/pybotvac) library*

## How it works

Plugin provides: Status, Control and schedule status devices

**Status**: show current status in readable layout of switch. Status updates by polls 
(interval) and when you click Control device (for instant status change)

**Control**: for sending commands

**Schedule**: for enable or disbled sheduled cleans


## Installation

Before installation plugin check the `python3`, `python3-dev`, `pip3` is installed for Domoticz plugin system:

```
sudo pip3 install pybotvac urllib3 requests
```

Then go to plugins folder and clone repository:
```
cd domoticz/plugins
git clone https://github.com/gilmrt/Domoticz-Botvac-Plugin.git
```

Only for Botvac D5 owners:
If you are using map, please add this step, if not go,to next step
```
git checkout BotvacD5
```

Restart the Domoticz service
```
sudo service domoticz restart
```

Now go to **Setup** -> **Hardware** in your Domoticz interface and add type with name **Botvac Vacuum**.

| Field | Information|
| ----- | ---------- |
| Neato email | Neato email account |
| Neato password | Neato password |
| Botvac vacuum name | The name of your Botvac vacuum |
| Debug | When set to true the plugin shows additional information in the Domoticz log |
| Update interval | In seconds, this determines with which interval the plugin polls the status of Vacuum. Minimun 10s. Default 60s   |

After clicking on the Add button the new devices are available in **Setup** -> **Devices**.

## How to update plugin

```
cd domoticz/plugins/Domoticz-Botvac-Plugin
git pull
```

Restart the Domoticz service
```
sudo service domoticz restart
```

## Screenshots
![](https://user-images.githubusercontent.com/4236800/80859999-1fb89f00-8c65-11ea-8b10-32316c23bfd2.png)


### Create a Neato account if not already done

Create a Neato account if not already done at [neatorobotics.com](https://neatorobotics.com/fr/my-neato-create-account/)
Then go to your [account](https://neatorobotics.com/fr/my-neato/)
or 
Use the Neato mobile app

