import subprocess
import time

def check_accelerometer():
    print("====================================")
    print("   MORSE - Accelerometer Test       ")
    print("====================================")
    print("Searching for AppleSPUHIDDevice in IOKit registry...")
    
    try:
        # ioreg lists all connected devices in the macOS I/O Kit registry
        result = subprocess.run(['ioreg', '-l'], capture_output=True, text=True, errors='ignore')
        
        if 'AppleSPUHIDDevice' in result.stdout:
            print("\n✅ SUCCESS: Accelerometer (AppleSPUHIDDevice) found on your Mac!")
            print("   The hardware is ready to be tapped.")
            print("\nNext step: We will use the 'hidapi' library to connect to this device ")
            print("and stream the live X, Y, Z vibration data in real-time.")
        else:
            print("\n❌ Accelerometer not found.")
            print("   Are you on an Apple Silicon (M1/M2/M3) Mac?")
            
    except Exception as e:
        print(f"\nError checking registry: {e}")

if __name__ == "__main__":
    check_accelerometer()
