import hid

print("====================================")
print("   MORSE - HID Enumeration          ")
print("====================================")
print("Looking for accelerometer HID device...\n")

found = False
for device in hid.enumerate():
    # Apple's vendor ID is usually 1452 (0x05ac)
    if 'AppleSPUHIDDevice' in device.get('product_string', '') or device.get('usage_page') == 0xFF00:
        found = True
        print("🎯 Found potential accelerometer device:")
        for key, value in device.items():
            print(f"   {key}: {value}")
        print("-" * 40)

if not found:
    print("Could not specifically identify 'AppleSPUHIDDevice' by name.")
    print("Here are ALL Apple HID devices found:")
    for device in hid.enumerate():
        if device.get('vendor_id') == 1452:  # 0x05ac
            print(f"Product: {device.get('product_string')}")
            print(f"  Path: {device.get('path')}")
            print(f"  Usage Page: {device.get('usage_page')} | Usage: {device.get('usage')}")
            print("-" * 40)
