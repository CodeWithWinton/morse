import os
import subprocess

def trigger_mac_mute():
    """Toggle macOS System Mute/Unmute using AppleScript"""
    script = 'set volume output muted not (output muted of (get volume settings))'
    subprocess.run(["osascript", "-e", script], check=False)

def trigger_apple_music_playpause():
    """Toggle Apple Music Play/Pause using AppleScript"""
    script = 'tell application "Music" to playpause'
    subprocess.run(["osascript", "-e", script], check=False)

def trigger_apple_music_next():
    """Next track on Apple Music"""
    script = 'tell application "Music" to next track'
    subprocess.run(["osascript", "-e", script], check=False)

def trigger_apple_music_prev():
    """Previous track on Apple Music"""
    script = 'tell application "Music" to previous track'
    subprocess.run(["osascript", "-e", script], check=False)

def trigger_raycast():
    """Launch Raycast / Spotlight launcher"""
    script = 'tell application "System Events" to key code 49 using {option down}'
    subprocess.run(["osascript", "-e", script], check=False)

def trigger_whatsapp():
    """Smart WhatsApp Toggle: Open/focus if hidden/background, Hide (Cmd+H) if active."""
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

def trigger_whatsapp_open():
    """Open/focus WhatsApp."""
    script = 'do shell script "open -a WhatsApp"'
    subprocess.run(["osascript", "-e", script], check=False)

def trigger_whatsapp_hide():
    """Hide WhatsApp (Cmd+H)."""
    script = '''
    tell application "System Events"
        set visible of process "WhatsApp" to false
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)

def execute_action(action_name="mute"):
    if action_name == "mute":
        print("🔊 Executing Action: MUTE / UNMUTE TOGGLE")
        trigger_mac_mute()
    elif action_name in ["music", "apple_music"]:
        print("🎵 Executing Action: APPLE MUSIC PLAY / PAUSE")
        trigger_apple_music_playpause()
    elif action_name == "whatsapp":
        print("💬 Executing Action: SMART WHATSAPP TOGGLE (OPEN / HIDE)")
        trigger_whatsapp()
    elif action_name == "whatsapp_open":
        print("💬 Executing Action: OPEN WHATSAPP")
        trigger_whatsapp_open()
    elif action_name == "whatsapp_hide":
        print("💬 Executing Action: HIDE WHATSAPP")
        trigger_whatsapp_hide()
    elif action_name == "next":
        print("⏭️ Executing Action: APPLE MUSIC NEXT TRACK")
        trigger_apple_music_next()
    elif action_name == "prev":
        print("⏮️ Executing Action: APPLE MUSIC PREVIOUS TRACK")
        trigger_apple_music_prev()
    elif action_name == "raycast":
        print("🚀 Executing Action: LAUNCH RAYCAST")
        trigger_raycast()

if __name__ == "__main__":
    print("Testing macOS Action Module...")
    execute_action("mute")
