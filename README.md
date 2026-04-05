# lancaster

> oh some tests are failing? lets remove the bad tests!!

<img src="https://www.lancaster.ac.uk/media/lancaster-university/content-assets/images/external-relations/hero-background-panel-and-simple-image/Lancaster-Castle-skyline-landing-hero.jpg" width="100%" alt="Lancaster Panorama" />

because it **casts** audio. over a **lan**. so its a **lancaster**... please laugh

# what is this?

fairly simple(ish) portable cross-platform python script for transmitting/recieving audio over a local network, kinda like airplay/dante/airfoil just without the paywalls, and/or hardware/brand requirements, and with more deep customisation. 

made for my [a-level computer science coursework](https://www.ocr.org.uk/qualifications/as-and-a-level/computer-science-h046-h446-from-2015/), however I do intend to use this myself, hence why I chose to make this instead of a game

I highly doubt anybody will interact with this repo whilst I'm working on it but I do feel the need to mention that, until the project has been submitted & graded, I will not be looking at or accepting pull requests/issues etc, since this does have to be my work and my work only. Its only public since it's something I find useful and so someone else somewhere probably will as well :)

once I've finished my course I'll convert the writeup over to markdown, redact bits of it like candidate & centre name & number and stick it here (if I remember) :D

# requirements

### from pip (check requirements.txt)

install with `pip3 install -r requirements.txt` or just `pip` if your system is configured that way. if not using a venv you may need to pass `--break-system-packages` but do so at your own risk. I have personally never had a problem but that doesn't mean you won't.

- numpy
- sounddevice

### not from pip (don't check requirements.txt)

- tkinter (install with `brew install python3-tk` or similar)
- portaudio (install with `sudo apt install libportaudio2` or similar)

# screenshots

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/macos-dual.png" width="100%" alt="loopback lancaster running on macOS 15" />

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/popos-dual.png" width="100%" alt="loopback lancaster running on pop!_os 24 (linux)" />

<img src="https://raw.githubusercontent.com/aroasanight/lancaster/refs/heads/main/readme-assets/windows-dual.png" width="100%" alt="loopback lancaster running on windows 11" />