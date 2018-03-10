# Liteup

This library should let you create a web-controlled APA102 LED strip, with logic driven by a Raspberry Pi.
There's a server component, which gives you a webpage that can issue commands to your raspberry pi. That can be hosted on any website, and even the pi itself.

There's also a client library, with a bunch of useful themes designed. You can add your own themes, with arguments such as colors, intensity, time, etc, and they'll be automatically added to the webserver.  It's intended to make this kind of project easy to do, and to customize!

(That's the dream. Currently - nothing exists yet. )



---
 #Liteup is a fork of the great [APA102 library by tinue](https://github.com/tinue/APA102_Pi).

It contains a lot of code from APA102, but also a significant number of more themes, as well as a server and client for web-control.

If you are looking to get started with APA102 LED strips, I highly recommend tinue's readme. I followed it pretty much exactly, with the exception that I did not use a level shifter, and controlled my APA102's with my Raspberry Pi's 3.3v out.
