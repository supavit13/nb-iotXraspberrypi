# nb-iotXraspberrypi
## requiremant
- pyserial
- python3
## run on startup
- sudo crontab -e

- add command to run script

@reboot python3 file.py 127.0.0.1 6000 1 &

*set you ip , port and node_number
