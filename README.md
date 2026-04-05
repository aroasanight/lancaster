# lancaster

> oh some tests are failing? lets remove the bad tests!!

**IMPORTANT:**
I highly doubt anybody will interact with this repo whilst I'm working on it but I do feel the need to mention that, since this is part of my coursework, until the project has been submitted & graded, I will not be looking at or accepting pull requests/issues etc, since this does have to be my work and my work only. It's public since it's something I find useful and so someone else somewhere probably will as well, and once I've completed the course I will start accepting stuff :)

<img src="https://www.lancaster.ac.uk/media/lancaster-university/content-assets/images/external-relations/hero-background-panel-and-simple-image/Lancaster-Castle-skyline-landing-hero.jpg" width="100%" alt="Lancaster Panorama" />

because it **casts** audio. over a **lan**. so its a **lancaster**... please laugh

# contents

* [what is this?](#what-is-this) - description of this project and why I made it
* [requirements](#requirements) - required libraries/software for lancaster to run
* [screenshots](#screenshots) - _ooh pretty_
* [components of the UI](#components-of-the-ui) - list of all components of the main UI
    * [top settings](#top-settings)
    * [network config](#network-config)
    * [audio config](#audio-config)
    * [buffer/gain config](#buffergain-config)
    * [bottom buttons](#bottom-buttons)
* [more details on the settings](#more-detail-on-the-settings)
    * [config file path](#config-file-path)
    * [connect/disconnect or listen/ignore](#connectdisconnect-or-listenignore)
    * [target IP](#target-ip)
    * [port](#port)
    * [nic selection](#nic-selection)
    * [input device & output device](#input-device--output-device)
    * [channel count](#channel-count)
    * [sample rate](#channel-count)
    * [buffer size](#buffer-size)
    * [tolerance](#tolerance)
    * [gain](#gain)

# what is this?

fairly simple(ish) portable cross-platform python script for transmitting/recieving audio over a local network, kinda like airplay/dante/airfoil just without the paywalls, and/or hardware/brand requirements, and with more deep customisation. 

made for my [a-level computer science coursework](https://www.ocr.org.uk/qualifications/as-and-a-level/computer-science-h046-h446-from-2015/), however I do intend to use this myself, hence why I chose to make this instead of a game like the majority of students do

> once I've finished my course I'll convert the writeup over to markdown, redact bits of it like candidate & centre name & number and stick it here (if I remember) :D

# requirements

### from pip (check requirements.txt)

install with `pip3 install -r requirements.txt` or just `pip` if your system is configured that way. if not using a venv you may need to pass `--break-system-packages` but do so at your own risk. I have personally never had a problem but that doesn't mean you won't.

* numpy
* sounddevice

### not from pip (don't check requirements.txt)

* tkinter (install with `brew install python3-tk` or similar)
* portaudio (install with `sudo apt install libportaudio2` or similar)

# screenshots

macOS 15.7.4 (Sequoia)

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/macos-dual.png" width="100%" alt="loopback lancaster running on macOS 15" />

Linux (pop!_OS 24.04)

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/popos-dual.png" width="100%" alt="loopback lancaster running on pop!_os 24 (linux)" />

Windows 11 24H2 (IoT Enterprise LTSC)

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/windows-dual.png" width="100%" alt="loopback lancaster running on windows 11" />

# components of the UI

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/ui.png" width="60%" alt="screenshot of lancaster's UI" />

from top to bottom - scroll down to the "more detail" section if you want to know more

### top settings
* [config file path](#config-file-path)
* mode toggle
* [connect/disconnect](#connectdisconnect-or-listenignore) buttons to connect to a listening receiver (these change to listen/ignore in receiver mode)

### network config
* [target IP](#target-ip) (only applicable in transmitter mode)
* [port](#port) (this changes to open port on receiver)
* [nic selection](#nic-selection)

### audio config
* [input device](#input-device--output-device) (configurable on transmitter at all times, and on reciever when paired to a transmitter)
* [output device](#input-device--output-device) (configureable on reciever at all times, and on transmitter when paired to a reciever)
* [channel count](#channel-count)
* [sample rate](#channel-count)

### buffer/gain config
* [buffer size](#buffer-size)
* [tolerance](#tolerance)
* [gain](#gain)

### bottom buttons
* start/stop (start/stop transmission once devices are paired, can be pressed from either device)
* toggle stats window (brings up the stats window)
* avg/error values (avg actual buffer size, and difference between actual and specified buffer sizes)
* status & health

# more detail on the settings

### config file path
* currently requires you to select an existing file
* if you need a second save file, copy your existing config and edit in a text editor or download sample-config.json from this repo
* data for both transmitter and reciever modes are stored in the same file
    * settings that overlap between the two (such as NIC selection and port) are stored twice, once for transmitter mode and once for reciever

### connect/disconnect or listen/ignore
* the receiver must be listening before attempting to connect from the receiver

### target IP
* only needed for transmitter
* specify IP of receiver to attempt to connect to

### port
* "open port" on receiver indicates the port to open on the receiver, "port" on the transmitter specifies the port specified on the reciever to attempt to connect to
* limited to ports ≥ 1024 and ≤ 65535
* if default port (5005) is unavailiable, pick a random port in that range you don't mind using - as long as it's consitent on both sides and it's between the values above and it's not taken by another program on your computer there is no reason it matters
* if you don't know what this does, leave it at default unless it says port is in use/taken etc then specify a random number in like the 50,000 range for lower likelihood of collisions

### nic selection
* useful in a show environment where your computer may be connected to both a show control network and an internet-conencted network, such as a guest wifi for the venue
– as of right now this doesn't force traffic through that nic - it kind of just nudges the OS in the right direction
* safe to leave on default unless it errors or devices can't find each other
* both transmitter and reciever's selected NICs if not both set to 0.0.0.0 must be on the same LAN and able to see each other on the network

### input device & output device
* sometimes displayed device doesn't reflect actual selected device
    * if this happens, just reselect the device on either end (this also fixes incosistencies in displayed devices on both ends)
* the local device (input for transmitter, output for receiver) is configurable when disconnected, remote device only when connected

### channel count
* both input and output devices must have the number of channels you specify here, or more. ie if you transmit all 8 channels from an audio interface, your output device must also have 8ch or more availiable to output to
* if you don't know how many you need, 1 means mono and 2 means stereo. if you needed to use anything beyond that you'd know

### sample rate
* list shows all sample rates supported by lancaster regardless of whether your in/out devices support it or not
* you must select a sample rate that is supported by both input and output devices
    * if you don't know what this does and one of your devices don't support 48k, try 44.1k instead as this is the second most common
    * some bluetooth devices if they have a microphone that is in use limits the sample rate of the output to 16k instead, so make sure the mic isn't in use (or use 16k but this is too low quality for most situations)

### buffer size
* specify the ideal amount of audio to be buffered by the reciever
    * increase this if you have frequent jitters/dropouts etc
    * decrease this if you have too large a latency between transmitting and hearing the audio

### tolerance
* distance from the specified buffer size that the actual amount of audio buffered is allowed to stray before drift correction kicks in
    * drift correction is characterised by very very minimal "clicks" in the audio, from it repeating tiny bits of audio or skipping tiny bits of audio in an effort to lengthen/shorten the amount of audio in the buffer
* unchecking the box "disables" drift correction (behind the scenes it just sets it to a large number so under realistic circumstances it would never reach the threshold)

### gain
* multiplier of the volume of the outputted audio
* this is applied at the transmitter end, as a simple multiplier to whatever comes out of the buffer
