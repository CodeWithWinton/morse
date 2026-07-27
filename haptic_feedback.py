import os
import sys
import time
import ctypes

DYLIB_PATH = os.path.join(os.path.dirname(__file__), "haptic_bridge.dylib")
try:
    libhaptic = ctypes.CDLL(DYLIB_PATH)
    libhaptic.fire_haptic_native.argtypes = [ctypes.c_long]
    libhaptic.fire_haptic_native.restype = None
except Exception as e:
    libhaptic = None

def fire_haptic(pattern=0):
    """
    Fires native Force Touch Trackpad haptic click (and optional click feedback).
    pattern 0: Generic Click
    pattern 1: Alignment Snapping Click
    pattern 2: Level Change Click
    """
    if libhaptic:
        try:
            libhaptic.fire_haptic_native(pattern)
            return True
        except Exception:
            pass
            
    # System Audio Click Indicator (Fired AFTER detection as user feedback)
    try:
        os.system("afplay /System/Library/Sounds/Pop.aiff &")
    except Exception:
        pass
        
    return False

def fire_double_tap_confirmation():
    """Fires a crisp double-haptic click confirmation."""
    fire_haptic(0)
    time.sleep(0.08)
    fire_haptic(1)

if __name__ == "__main__":
    print("==========================================================")
    print("  MORSE - Native Trackpad Haptic Feedback Test            ")
    print("==========================================================")
    print("🖐️ Rest your hand lightly on the Force Touch Trackpad!")
    print("Firing 3 test haptic clicks in 1 second...\n")
    time.sleep(1.0)
    
    print("📳 Click 1: Generic Click...")
    fire_haptic(0)
    time.sleep(0.5)
    
    print("📳 Click 2: Alignment Click...")
    fire_haptic(1)
    time.sleep(0.5)
    
    print("📳 Click 3: Double-Tap Confirmation Click-Click...")
    fire_double_tap_confirmation()
    print("\n✅ Haptic test finished cleanly!")
