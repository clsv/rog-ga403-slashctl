# GA403 Slash Lighting Controller (Python)

A Python utility to control the *Slash* LED lighting of the ASUS ROG GA403 series.

This implementation is based on reverse-engineered command sequences from [`seerge/g-helper`](https://github.com/seerge/g-helper) and communicates directly with the USB HID interface of the device.

---

## 📦 Requirements

Make sure the following packages are installed:

```bash
sudo apt install libhidapi-libusb0 python3-hid python3
```

## Udev Rules (Optional, Recommended)
To allow non-root access to the device:

Create a file: /etc/udev/rules.d/99-asus-ite.rules with the following content:
```
SUBSYSTEM=="usb", ATTRS{idVendor}=="0b05", ATTRS{idProduct}=="19b6", MODE="0666", GROUP="plugdev"
```

Then reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Device Info
- **Vendor ID:** `0x0b05` (ASUSTek Computer, Inc.)
- **Product ID:** `0x19b6` (ITE Device 8910)
- **Tested on:** ASUS ROG GA403 series

## Usage
```bash
python3 slashctl.py --enable true
python3 slashctl.py --battery
python3 slashctl.py --brightness 10 --mode Phantom
```

## Available Options
| Argument       | Description                                   |
| -------------- | --------------------------------------------- |
| `--enable`     | Enable or disable the device (`true`/`false`) |
| `--brightness` | Set brightness level (`0`–`10`)               |
| `--mode`       | Set animation mode (see list below)           |
| `--battery`    | Show battery level animation                  |

Supported Modes
```
Bounce, Slash, Loading, BitStream, Transmission,
Flow, Flux, Phantom, Spectrum, Hazard,
Interfacing, Ramp, GameOver, Start, Buzzer,
Static, BatteryLevel
```

## Examples
### Enable slash lighting
```
python3 slashctl.py --enable true
```

### Set brightness and mode
```
python3 slashctl.py --brightness 8 --mode Transmission
```

### Show battery charge level
```
python3 slashctl.py --battery
```

### Disable lighting
```
python3 slashctl.py --enable false
```

## Status

- [x] Basic lighting modes
- [x] Brightness control
- [x] Battery level animation
- [ ] Static custom pattern
