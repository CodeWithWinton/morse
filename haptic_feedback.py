import sys
import time
import ctypes
import ctypes.util

# Load AppKit framework for NSHapticFeedbackManager
appkit = ctypes.cdll.LoadLibrary(ctypes.util.find_library("AppKit"))
objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))

# Objective-C method signature bindings
objc.objc_getClass.restype = ctypes.c_void_p
objc.objc_getClass.argtypes = [ctypes.c_char_p]

objc.sel_registerName.restype = ctypes.c_void_p
objc.sel_registerName.argtypes = [ctypes.c_char_p]

objc.objc_msgSend.restype = ctypes.c_void_p
objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

NSHapticFeedbackManager = objc.objc_getClass(b"NSHapticFeedbackManager")
defaultPerformer_sel = objc.sel_registerName(b"defaultPerformer")
perform_sel = objc.sel_registerName(b"performFeedbackPattern:performanceTime:")

# Setup performFeedbackPattern argument types
perform_msgSend = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_long,  # NSHapticFeedbackPattern
    ctypes.c_long   # NSHapticFeedbackPerformanceTime
)(objc.objc_msgSend)

def fire_haptic(pattern=0):
    """
    Fires a native Force Touch Trackpad haptic click.
    pattern 0: Generic Click
    pattern 1: Alignment Snapping Click
    pattern 2: Level Change Click
    """
    try:
        performer = objc.objc_msgSend(NSHapticFeedbackManager, defaultPerformer_sel)
        if performer:
            perform_msgSend(performer, perform_sel, pattern, 0)
            return True
    except Exception as e:
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
    print("\n✅ Haptic test finished!")
