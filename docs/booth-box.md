Booth-in-a-Box Setup
====================
Using as a thin-client for karakara.uk

Parts:

* Raspberry Pi 4B
* USB-C power supply
* 7" touchscreen
* Case for touchscreen + pi
* 4GB+ MicroSD card
* MicroHDMI <-> HDMI cable
* (USB mouse & keyboard, for initial setup)

One-time steps:

* Install raspbian on SD card, insert card into pi
* Assemble pi / screen / case
* Boot, do basic setup (eg wifi, software updates)
* Edit `/boot/config.txt` - set `lcd_rotate=2`, reboot
* run `raspi-config`, Performance, GPU Memory, set to 512MB
  (Is this actually needed? How much exactly is needed? Note that it seems
  external displays are only detected at boot, no hot-plugging...)
* Copy [booth.sh](./scripts/booth.sh) to the pi's home directory
* To launch karakara on boot, create `~/.config/lxsession/LXDE-pi/autostart`, add:
```
@lxpanel --profile LXDE-pi
@bash /home/pi/booth.sh
```
* MAYBE: chrome on-screen keyboard?

Each-time steps:

* Open up [player2](https://karakara.uk/player2/) on the projector,
  double-click title to set room / password / fullscreen
* Open up [browser2](https://karakara.uk/browser2/) touchscreen,
  double-click title to set room / password / fullscreen
