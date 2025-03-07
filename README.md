# Icarus-Lite
Icarus Lite is a lightweight and easy-to-use version of the ChromeOS unenrollment exploit known as Icarus, which unenrolls devices with device management interception using a proxy and a custom Certificate Authority.
<br>
> Icarus Lite is based off the [original Icarus](https://github.com/MunyDev/icarus) code and works in the same way. Although the original Icarus is currently archived and no longer recieving support, Icarus Lite will be supported and updated.
## Warnings
- Icarus AND Icarus Lite <b>only</b> work on ChromeOS versions below 130. If you are above v130, please downgrade to use Icarus/Icarus Lite.
- Icarus Lite has <b>not been fully tested</b> as of March 7th, 2025. If you encounter issues while using, please create an Issue.
- Do not use any public Icarus proxies. Icarus can be used maliciously to remotely manage and track devices. Icarus Lite is intended to be simple to use, and self-hosting Icarus is heavily advised over using any public proxies.
- Icarus Lite does <b>NOT</b> currently have functionality to build Icarus shims. Please download a prebuilt shim to use Icarus Lite, or refer an Icarus fork for information on manually building shims.

## Setup Instructions
### Windows
If you are on Windows, you can download a pre-compiled .exe version of Icarus in the "Releases" section of this repository. Alternatively, you can follow the Linux/Mac instructions below to manually build Icarus on your machine.
### Linux/Mac
If you are on Linux or Mac (or wish to run Icarus Lite from its source directly on Windows), the below instructions will cover how to run Icarus Lite.
1. Open a Command Prompt/Terminal window and run ``python --version`` and/or ``python3 --version``. If the command is not found, install Python from [python.org](https://python.org/downloads) (or wherever/however is best for your OS/distro). Once Python has been installed, <b>close and re-open a new terminal.</b>
2. Install the ``protobuf`` Python package, which can be done by running ``pip install protobuf`` and/or ``pip3 install protobuf``. On some Linux distros (specifically in managed environments), pip may not work correctly, in which case you may need to use ``sudo apt install python3-protobuf``.
3. Run ``git --version``. If the command is not found, install Git from [git-scm.com](https://git-scm.com/downloads) (or wherever/however is best for your OS/distro). Once Git has been installed, <b>close and re-open a new terminal.</b>
4. In whichever directory you want to copy Icarus Lite into, run ``git clone https://github.com/cosmicdevv/Icarus-Lite.git``, then run ``cd Icarus-Lite``.
5. Run ``python main.py`` and/or ``python3 main.py``.
6. Icarus Lite will attempt to automatically set up the required file structure and download the latest SSL certificates from kxtz's Icarus fork.
<details>
  <summary>Icarus Lite failing to download certificates?</summary>
  You will need to manually download the certificates from a proper source (recommended to use kxtz's Icarus fork) and place them into ``Icarus Lite/manualcerts``.
</details>

## Usage Instructions
Once Icarus Lite is running, usage is extremely simple. <b>Icarus Lite will attempt to automatically fetch your local IP when the Proxy Server starts, and will provide you with an IP and port to use.</b> Using Icarus Lite on the target ChromeOS device is the same process as using normal Icarus assuming the device's Stateful Partition has already been modified by an Icarus shim. <b>The target ChromeOS device should be on the SAME network as the device hosting the Icarus Lite server.</b>
1. After rebooting into ChromeOS verified mode following using an Icarus shim, <b>do not click "continue"</b>. Instead, manually open the Network Configuration by clicking on the bottom-right icons which contain the time, WiFi, and Battery status. Once in Network Configuration, connect to your WiFi and enter the proxy settings.
2. Set "Connection Type" to Manual
3. Set the "Secure HTTP" IP address to the IP Icarus Lite gives you
4. Set the "Secure HTTP" port to the port Icarus Lite gives you
5. Click "Save"
6. Resume the ChromeOS setup process as normal and Icarus Lite should unenroll you.
<details>
  <summary>Device still enrolling/getting "Can't reach Google"?</summary>
  - Make sure that Icarus Lite is recieving and handling the ChromeOS device's requests; check the terminal/window where Icarus Lite is running for any output past "Icarus LITE is running on...". If nothing else has been output, it means Icarus Lite isn't recieving requests from the Chromebook and therefore is not handling them accordingly. In this case, re-run the Icarus shim and ensure:
    - The target ChromeOS device and the device hosting the proxy are on the <b>SAME</b> WiFi network
    - a
</details>

## Credits
- [cosmicdevv](https://github.com/cosmicdevv) - Writing and maintaining Icarus Lite
- [MunyDev](https://github.com/MunyDev) - Discovering and creating original Icarus
- [Fanqyxl](https://github.com/fanqyxl) - new maintainer
- [kxtzownsu](https://github.com/kxtzownsu) - Maintaining certificates Icarus uses
