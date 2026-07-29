"""
MORSE TLM 1.5 — Universal Cross-Platform Action Handlers
=========================================================
Supports macOS, Windows, and Linux.
"""
import os
import sys
import platform
import subprocess

PLATFORM = platform.system()  # "Darwin", "Windows", "Linux"


def _run_osascript(script):
    """Run an AppleScript command (macOS only)."""
    subprocess.Popen(["osascript", "-e", script])


def trigger_media_playpause():
    """Toggle Play/Pause for the active media player on any OS."""
    if PLATFORM == "Darwin":
        # macOS: Directly tell running media app to playpause (no terminal key bleed)
        script = '''
        if application "Spotify" is running then
            tell application "Spotify" to playpause
        else if application "Music" is running then
            tell application "Music" to playpause
        end if
        '''
        _run_osascript(script)
    elif PLATFORM == "Windows":
        # Windows: Send VK_MEDIA_PLAY_PAUSE (0xB3) via PowerShell
        subprocess.Popen(["powershell", "-Command",
            "(New-Object -ComObject WScript.Shell).SendKeys([char]0xB3)"])
    elif PLATFORM == "Linux":
        # Linux: Use playerctl or xdotool
        subprocess.Popen(["playerctl", "play-pause"])


def trigger_whatsapp():
    """Smart WhatsApp Toggle: Open/focus if hidden, hide if active."""
    if PLATFORM == "Darwin":
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell
        if frontApp is "WhatsApp" then
            tell application "System Events" to set visible of process "WhatsApp" to false
        else
            do shell script "open -a WhatsApp"
        end if
        '''
        subprocess.run(["osascript", "-e", script], check=False)
    elif PLATFORM == "Windows":
        # Windows: Toggle WhatsApp UWP or Desktop app
        subprocess.Popen(["powershell", "-Command",
            'Start-Process "whatsapp:"'])
    elif PLATFORM == "Linux":
        subprocess.Popen(["xdg-open", "https://web.whatsapp.com"])


def trigger_screenshot():
    """Take a native screenshot on any OS."""
    if PLATFORM == "Darwin":
        _run_osascript('tell application "System Events" to key code 20 using {command down, shift down}')
    elif PLATFORM == "Windows":
        subprocess.Popen(["powershell", "-Command",
            "(New-Object -ComObject WScript.Shell).SendKeys('{PRTSC}')"])
    elif PLATFORM == "Linux":
        subprocess.Popen(["gnome-screenshot"])


def trigger_mute():
    """Toggle system mute on any OS."""
    if PLATFORM == "Darwin":
        _run_osascript('set volume output muted not (output muted of (get volume settings))')
    elif PLATFORM == "Windows":
        subprocess.Popen(["powershell", "-Command",
            "(New-Object -ComObject WScript.Shell).SendKeys([char]0xAD)"])
    elif PLATFORM == "Linux":
        subprocess.Popen(["amixer", "set", "Master", "toggle"])


def execute_action(action_name="whatsapp"):
    """Dispatch action by name."""
    dispatch = {
        "whatsapp": trigger_whatsapp,
        "media": trigger_media_playpause,
        "playpause": trigger_media_playpause,
        "screenshot": trigger_screenshot,
        "mute": trigger_mute,
    }
    fn = dispatch.get(action_name)
    if fn:
        fn()


if __name__ == "__main__":
    print(f"Platform: {PLATFORM}")
    print("Testing Media Play/Pause...")
    trigger_media_playpause()
