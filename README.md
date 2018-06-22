# nb-iotXraspberrypi
## requiremant
- pyserial
- python3
- dump1090-fa by flightaware
## installation
- connect R820T2 ADS-B receiver , NB-IoT Shield and power supply to your pi
- install python3, pyserial and dump1090-fa then reboot your pi
- setup true_nb_iot_bc95.py on startup following below step

## run on startup
- sudo crontab -e

- add command to run script

  @reboot python3 file.py [IP] [PORT] [NODE_NUMBER] &



- reboot your pi

Note : set you ip , port and node_number

Ex: @reboot python3 file.py 127.0.0.1 6000 1 &
