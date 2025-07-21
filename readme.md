# Throughputter

A simple graphical UI to iperf for Android device throughput testing.

## Description

Designed to run iperf DL/UL throughput tests on Android-based devices, over adb protocol. This tool provides an intuitive interface for configuring and executing iperf commands on connected Android devices.

## Features

* Connect to Android devices via ADB
* Configure all major iperf parameters through a user-friendly interface
* Support for both server (DL) and client (UL) modes
* UDP and TCP protocol support
* Command logging and result saving
* Copy commands to clipboard for external use

## Getting Started

### Dependencies

* An Android-based DUT with iperf installed in data/iperf directory
* Path to the Android SDK Platform-Tools directory in system's PATH environment variable
* Python 3.6 or higher
* Required Python packages (install via `pip install -r requirements.txt`):
  * pure-python-adb==0.3.0.dev0
  * pyperclip==1.9.0

### Installation

1. Clone this repository or download the source code
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Executing program

1. Plug DUT over USB serial port
2. Run the application:
   ```
   python main.py
   ```
3. Click "Get devices" to detect connected Android devices
4. Select your device from the dropdown list
5. Adjust iperf command with parameters provided or adjust it manually
6. Specify directory to save test logs if necessary
7. Click "Run iperf" to execute the command

## Usage Tips

* **Server Mode (DL)**: Tests download throughput to the Android device
* **Client Mode (UL)**: Tests upload throughput from the Android device
* **UDP/TCP**: Toggle between UDP and TCP protocols
* **Bandwidth**: Set target bandwidth (e.g., "100m" for 100 Mbps)
* **Time**: Set test duration in seconds
* **Interval**: Set reporting interval in seconds
* **Log output**: Enable to save test results to a file


## Authors

m.banaszczyk

## Version History

* 1.0
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.