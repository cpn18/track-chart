# Setting Up a Local Instance

If your work does not require loading data for ReactApp changes you can run `npm run start` instead of following the steps below.

## Environment Setup

### Manual

Manually install the required python and ReactApp dependencies

### Using Nix

Recommended for dveloping on Linux and Mac, it will do all the hard work for you.

For windows [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) is required

1) [install nix](https://nixos.org/download/) (the package manager)
2) `mkdir -p ~/.config/nix`
3) `echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf`
   - If you're using NixOs, you've probably already enabled flakes in your config, if not or if the above instructions don't work [follow these directions](https://nixos.wiki/wiki/flakes)
4) run `nix develop` inside the repository 
   - this will setup the environment for you, remember to run it every time you use the project
   - to more quickly get to your editor of choice you can run `nix develop --command <editor>` (e.g. `nix develop --command code .`)

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
2) When done exit the launcher TUI with `ctrl+c`
