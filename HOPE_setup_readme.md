following headless pi setup:

*Kit required*
    Raspberry pi zero W
    Power adaptor for it
    apa102 leds that match the amount of power you have
    microsd chip
    microsd adaptor
    Data-capable USB cable


https://medium.com/@aallan/setting-up-a-headless-raspberry-pi-zero-3ded0b83f274

    this may also be helpful
    https://hackernoon.com/raspberry-pi-headless-install-462ccabd75d0


download latest version
raspbarian lite
https://www.raspberrypi.org/downloads/raspbian/

write image to sd card
(I use etcher on osx)

add ssh
 (don't add a wpa_supplicant at this point, we'll do that post boot. The reason is we want to boot and change the hostname to something unique, so everyone is sshing into their own pi)

- The next two steps enable ethernet over usb on the pi

    - config.txt
        add `dtoverlay=dwc2` as last line

    -cmdline.txt
        replace contents with
```
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=4d3ee428-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait modules-load=dwc2,g_ether quiet init=/usr/lib/raspi-config/init_resize.sh
```


- eject sd card
- insert into pi

- plug data usb into pi (middle port) and computer.
- wait 1 min for boot
- try to find pi on the network, here are some ways:

(
You may want to disconnect from the wifi to do this. The connection goes over the usb which emulates ethernet.
If you don't disconnect from the wifi you may log into your neighbors raspberry pi.
)

`ping raspberrypi.local`
`dns-sd -G v4 raspberrypi.local`

You should be able to ssh into the pi, and get a shell on it. If that doesn't work, we can use nmap to find it and log in with the ip.
When I did this, my pi had an IP of `169.254.221.175`.


`ssh pi@raspberrypi.local`
or
`ssh pi@169.254.221.175` (whatever the IP address is)


username: pi
password: raspberry

if it doesn't respond to ssh, maybe the ip address is wrong, or maybe you forgot to make a `ssh` file?

~~~~~ Once you're in ~~~~~~

You have a few tasks here:
There are two annoying text editors built in vi and nano. You can use either to edit these files. Once we edit them we'll enable wifi and you can download a better text editor.

- Change the hostname so it's different than your classmates.

Just something unique and simple. Replace this file
`sudo vi /etc/hostname`
also replace the hostname in this file with your new name
`sudo vi /etc/hosts`

- change the password (optional but wise)
`passwd`

- configure wireless if you haven't already
/etc/wpa_supplicant/wpa_supplicant.conf
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
       ssid="SSID"
       psk="PASSWORD"
       key_mgmt=WPA-PSK
    }
```

Then... REBOOT!
you should have a individually named raspberry pi on the wifi network now. Log in with your new hostname
make sure you can see google:
`ping www.google.com`


- install convenience packages

`sudo apt-get install vim`
or
`sudo apt-get install emacs`

- install dependencies
`sudo apt-get install git`

- install berryconda - this is our python distribution
    (https://github.com/jjhelmus/berryconda). We will be using python 3.6
    ```
    wget https://github.com/jjhelmus/berryconda/releases/download/v2.0.0/Berryconda3-2.0.0-Linux-armv6l.sh
    chmod +x Berryconda3-2.0.0-Linux-armv6l.sh
    ./Berryconda3-2.0.0-Linux-armv6l.sh
    ```
- configure pi to use hardware spi
    `sudo raspi-config`, Interfacing Options, SPI, Enable

- install liteup https://github.com/mcscope/liteup
    - (optionally) fork the repo on github. This will allow you to publish your changes
    - either:
    `git clone https://github.com/mcscope/liteup.git`
    or
    `git clone https://github.com/<yourrepo>/liteup.git`

    We are using the https versions for simplicity but if you want to do a lot of development and write your own patterns, it's worth making a fork and using the ssh versions and adding the ssh key so you can push without a password. If you don't know what this message means, you can ignore it and use https.

    `cd liteup`
    - Install liteup locally with pip, including dependencies
    `conda install scipy`
    `pip install -e .`
- edit config file
- wire it up
- run liteup for the first time
`python client.py fullscan`

- set liteup to auto-run
    - TODO install the provided systemd files

- editing on pi:
you can either use vim/emacs to edit on the pi, or if you are used to a visual text editor, you can use the `sshfs` program (needs to be installed) to mount the raspberry pi as a local drive.

- write your first scheme!

TODO systemd
