Booth-in-a-Box Setup
====================
Using as a thin-client for karakara.org.uk

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
* MAYBE: chrome on-screen keyboard?

Each-time steps:

* Open one chrome window, get admin cookie by logging in to [admin console]()
* Open up [player2](https://karakara.org.uk/player2/#queue_id=MY_QUEUE), fullscreen it on the projector
* Open up [browser2](https://karakara.org.uk/), fullscreen it on the touchscreen
