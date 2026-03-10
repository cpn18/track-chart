# Setting Up a Local Instance

If your work does not require loading data for ReactApp changes you can run `npm run start` instead of following the steps below.

## Environment Setup

## Code Changes
Please ensure that you do not commit these changes, as they are only applicable for development.

### Launcher
location: `gps-pi/launcher.sh`

1) Change `usb_drive` and `mount_point` variables to direct to a directory for logging
2) Create the directory, and within it a directory named `PIRAIL`
3) Comment out the call to `wait_for_gps_fix.py`

### Config
location: `gps-pi`

1) Copy `config_dev.json` to `gps-pi`, renaming to `config.json`
2) Under the `sim` entry set `data` to the path of the data to load

### ReactApp
location:  `ReactApp`

1) Run `npm run build`

## Running

1) Run `./gps-pi/launcher.sh`
2) When done kill all processes spawned by the launcher
