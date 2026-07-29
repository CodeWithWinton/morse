"""
MORSE TLM 1.5 — Universal Cross-Platform Audio Feedback
========================================================
Plays a short confirmation sound on tap detection.
macOS: System alert sound (Bottle.aiff / Bubble)
Windows: System asterisk beep
Linux: paplay or aplay fallback
"""
import platform
import subprocess

PLATFORM = platform.system()


def play_bubble_sound():
    """Triggers a native system confirmation sound on any OS."""
    try:
        if PLATFORM == "Darwin":
            subprocess.Popen(["osascript", "-e", "beep"])
        elif PLATFORM == "Windows":
            # Windows: Play system asterisk sound via PowerShell
            subprocess.Popen(["powershell", "-Command",
                "[System.Media.SystemSounds]::Asterisk.Play()"])
        elif PLATFORM == "Linux":
            # Linux: Try paplay (PulseAudio) then aplay (ALSA)
            try:
                subprocess.Popen(["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"])
            except FileNotFoundError:
                subprocess.Popen(["aplay", "/usr/share/sounds/alsa/Front_Center.wav"])
    except Exception:
        pass


def fire_double_tap_confirmation():
    """Fires native system confirmation sound."""
    play_bubble_sound()


def fire_haptic(pattern=0):
    play_bubble_sound()
    return True


if __name__ == "__main__":
    print(f"Platform: {PLATFORM}")
    print("🔊 Triggering system confirmation sound...")
    play_bubble_sound()
    print("✅ Done!")
