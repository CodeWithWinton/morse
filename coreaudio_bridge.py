import os
import subprocess
import ctypes
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
C_SRC = os.path.join(BASE_DIR, "coreaudio_bridge.c")
DYLIB_PATH = os.path.join(BASE_DIR, "coreaudio_bridge.dylib")

def build_dylib():
    """Compile coreaudio_bridge.c into a shared library using native clang."""
    if not os.path.exists(DYLIB_PATH) or os.path.getmtime(C_SRC) > os.path.getmtime(DYLIB_PATH):
        print("🛠️ Compiling native CoreAudio C bridge (coreaudio_bridge.dylib)...")
        cmd = [
            "/usr/bin/clang",
            "-shared",
            "-fPIC",
            "-framework", "CoreAudio",
            "-framework", "AudioToolbox",
            "-o", DYLIB_PATH,
            C_SRC
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ CoreAudio C Compilation Error:\n{result.stderr}")
            return False
        print("✅ CoreAudio dylib successfully compiled!")
    return True

def load_bridge():
    """Load the compiled dylib via ctypes and bind function signatures."""
    if not build_dylib():
        return None
    try:
        lib = ctypes.CDLL(DYLIB_PATH)
        lib.get_default_input_device.restype = ctypes.c_uint32
        lib.query_input_channels.argtypes = [ctypes.c_uint32]
        lib.query_input_channels.restype = ctypes.c_int
        return lib
    except Exception as e:
        print(f"❌ Failed to load CoreAudio dylib: {e}")
        return None

def inspect_coreaudio_hardware():
    """Query and print hardware stream details from CoreAudio HAL."""
    bridge = load_bridge()
    if not bridge:
        return -1
    dev_id = bridge.get_default_input_device()
    channels = bridge.query_input_channels(dev_id)
    return channels

if __name__ == "__main__":
    print("====================================")
    print("   MORSE - CoreAudio HAL Hardware Inspection")
    print("====================================")
    ch = inspect_coreaudio_hardware()
    print(f"\nResult: CoreAudio HAL presented {ch} input channel(s).")
