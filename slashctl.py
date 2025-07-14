#!/bin/env python3
import argparse
import hid
import time

VENDOR_ID = 0x0B05
PRODUCT_ID = 0x19B6  # or 0x193B for regular SlashDevice
REPORT_ID = 0x5D     # 0x5E for the regular model

def write_packet(device, payload: bytes, log=None):
    data = bytes([REPORT_ID]) + payload
    device.write(data)
    if log:
        print(f"{log}: {data[:16].hex()}")

def wakeup(device):
    write_packet(device, b"ASUS Tech.Inc.", "Wake1")
    write_packet(device, bytes([0xC2]), "Wake2")
    write_packet(device, bytes([0xD1, 0x01, 0x00, 0x01]), "Wake3")

def init(device):
    write_packet(device, bytes([0xD7, 0x00, 0x00, 0x01, 0xAC]), "Init1")
    write_packet(device, bytes([0xD2, 0x02, 0x01, 0x08, 0xAB]), "Init2")

def set_enabled(device, status: bool):
    write_packet(device, bytes([0xD8, 0x02, 0x00, 0x01, 0x00 if status else 0x80]), f"Enable {status}")

def save(device):
    write_packet(device, bytes([0xD4, 0x00, 0x00, 0x01, 0xAB]), "Save")

mode_codes = {
    "Static": 0x06,
    "Bounce": 0x10,
    "Slash": 0x12,
    "Loading": 0x13,
    "BitStream": 0x1D,
    "Transmission": 0x1A,
    "Flow": 0x19,
    "Flux": 0x25,
    "Phantom": 0x24,
    "Spectrum": 0x26,
    "Hazard": 0x32,
    "Interfacing": 0x33,
    "Ramp": 0x34,
    "GameOver": 0x42,
    "Start": 0x43,
    "Buzzer": 0x44,
}

def set_mode(device, mode_name: str):
    mode = mode_codes.get(mode_name)
    if mode is None:
        print(f"Unknown mode: {mode_name}")
        return
    write_packet(device, bytes([0xD2, 0x03, 0x00, 0x0C]), "Mode1")
    write_packet(device, bytes([
        0xD3, 0x04, 0x00, 0x0C, 0x01, mode,
        0x02, 0x19, 0x03, 0x13, 0x04, 0x11, 0x05, 0x12, 0x06, 0x13
    ]), "Mode2")

def set_custom(device, hexstr: str):
    data = bytes.fromhex(hexstr)
    if len(data) != 7:
        print("Custom pattern must be 7 bytes (14 hex digits)")
        return

    write_packet(device, bytes([0xD2, 0x02, 0x01, 0x08, 0xAC]), "C1")
    write_packet(device, bytes([0xD3, 0x03, 0x01, 0x08, 0xAC, 0xFF, 0xFF, 0x01, 0x05, 0xFF, 0xFF]), "C2")
    write_packet(device, bytes([0xD4, 0x00, 0x00, 0x01, 0xAC]), "C3")
    write_packet(device, bytes([0xD3, 0x00, 0x00, 0x07]) + data, "Custom")

def get_battery_percent():
    try:
        with open("/sys/class/power_supply/BAT1/capacity", "r") as f:
            return int(f.read().strip())
    except Exception:
        return 100

def get_battery_pattern(brightness, percent):
    bracket = int(percent / 14.2857)
    max_val = int(brightness * 85.333)
    pattern = [0x00] * 7
    for i in range(6, 6 - bracket, -1):
        pattern[i] = max_val
    if bracket < 7:
        part = ((percent % 14.2857) * max_val) / 14.2857
        pattern[6 - bracket] = int(part)
    return bytes(pattern)

def set_battery(device, brightness):
    percent = get_battery_percent()
    pat = get_battery_pattern(brightness, percent)
    set_custom(device, pat.hex())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--enable", type=str)
    parser.add_argument("--mode", type=str)
    parser.add_argument("--brightness", type=int, default=3)
    parser.add_argument("--custom", type=str)
    parser.add_argument("--battery", action="store_true")
    parser.add_argument("--save", action="store_true")

    args = parser.parse_args()

    try:
        device = hid.device()
        device.open(VENDOR_ID, PRODUCT_ID)
        device.set_nonblocking(1)
    except Exception as e:
        print("Failed to open device:", e)
        return

    wakeup(device)
    time.sleep(0.05)
    init(device)

    if args.enable is not None:
        set_enabled(device, args.enable.lower() == "true")

    if args.mode:
        set_mode(device, args.mode)

    if args.custom:
        set_custom(device, args.custom)

    if args.battery:
        set_battery(device, args.brightness)

    if args.save:
        save(device)

    device.close()

if __name__ == "__main__":
    main()
