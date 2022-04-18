Based on 2022-04-04-raspios-bullseye-arm64-lite.img

Keyboard Setup:
Other -> English (US)

Keyboard Layout:
English (US)

Username:
pirail

Password:
0nTr@ck

Configuration:
# raspi-config
8 Update
1 System
S4 Hostname: pirailv2
S5 Boot: B1
3 Interface Options
I2 SSH: Enable
I5 I2C: Enable
I6 Serial: Login=No, Enabled=Yes
6 Advanced Options
A1 Expand Filesystem
Finish, and reboot

