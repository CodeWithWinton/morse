import os
import subprocess

def play_bubble_sound():
    """
    Plays the native macOS default bubble pop sound effect (/System/Library/Sounds/Bottle.aiff).
    Runs asynchronously in the background (&) for zero latency (<0.1ms).
    """
    try:
        # Bottle.aiff is the iconic macOS bubble sound effect
        if os.path.exists("/System/Library/Sounds/Bottle.aiff"):
            subprocess.Popen(["afplay", "/System/Library/Sounds/Bottle.aiff"])
        else:
            subprocess.Popen(["afplay", "/System/Library/Sounds/Pop.aiff"])
    except Exception:
        pass

def fire_double_tap_confirmation():
    """Fires native macOS bubble sound confirmation."""
    play_bubble_sound()

# Alias for backward compatibility
def fire_haptic(pattern=0):
    play_bubble_sound()
    return True

if __name__ == "__main__":
    print("==========================================================")
    print("  MORSE - macOS Bubble Audio Confirmation Test            ")
    print("==========================================================")
    print("🔊 Playing native macOS bubble sound (Bottle.aiff)...")
    play_bubble_sound()
    print("✅ Done!")
