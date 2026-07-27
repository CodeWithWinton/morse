import hid
import struct
import time
import math
import sys
import os

print("====================================")
print("   MORSE - Direct HID Stream        ")
print("====================================")

# 1. Enforce Sudo (Root Access)
if os.geteuid() != 0:
    print("\n❌ PERMISSION ERROR: You MUST run this script with sudo!")
    print("Run: sudo python3 stream_data.py")
    sys.exit(1)

ACCEL_SCALE = 65536.0

def find_accelerometer():
    for device_info in hid.enumerate():
        if device_info['usage_page'] == 65280 and device_info['usage'] == 3:
            return device_info['path']
    return None

path = find_accelerometer()
if not path:
    print("\n❌ Accelerometer not found via HID.")
    sys.exit(1)

print(f"✅ Found accelerometer at path: {path}")

try:
    dev = hid.device()
    dev.open_path(path)
    
    # 2. Wait up to 1 second for data, otherwise loop
    dev.set_nonblocking(0) 
    print("🔓 Device opened successfully!")
    print("⏳ Waiting for data (Tap your Mac chassis!)... Press Ctrl+C to stop.\n")
    
    while True:
        # Read a 22-byte HID report from the sensor
        data = dev.read(22, timeout_ms=500)
        
        if not data:
            continue
            
        if len(data) >= 22:
            raw_bytes = bytes(data)
            # The accelerometer payload is located at byte index 6
            x, y, z = struct.unpack('<iii', raw_bytes[6:18])
            
            # Convert raw numbers to G-Force
            x_g = x / ACCEL_SCALE
            y_g = y / ACCEL_SCALE
            z_g = z / ACCEL_SCALE
            
            # Calculate total magnitude (vibration force)
            mag = math.sqrt(x_g**2 + y_g**2 + z_g**2)
            
            # Normal gravity is 1.0. We only print if it spikes above 1.05
            if mag > 1.05:
                print(f"💥 TAP DETECTED: Force = {mag:.3f} G")
                
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    dev.close()
    print("\nStopping...")
