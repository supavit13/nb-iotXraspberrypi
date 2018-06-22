# nb-iotXraspberrypi
## requiremant
- pyserial
- python3
## run on startup
- sudo crontab -e

- add command to run script

  @reboot python3 file.py [IP] [PORT] [NODE_NUMBER] &



- reboot your pi

Note : set you ip , port and node_number

Ex: @reboot python3 file.py 127.0.0.1 6000 1 &
