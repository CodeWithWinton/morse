import time
import hardware_guards

def main():
    print("==========================================================================")
    print("     MORSE - Hardware Event Guard & Suppression Diagnostic Suite          ")
    print("==========================================================================")
    print("🛡️  Starting Quartz CGEventTap background event listener...")
    hardware_guards.start_guards()
    print("Press Ctrl+C to exit.")
    print("👉 Try Typing on Keyboard, Pressing Space Bar, Moving/Scrolling Trackpad, or Pressing Fn key!\n")

    was_typing = False
    was_trackpad = False
    
    try:
        while True:
            current_time = time.time()
            is_typing = hardware_guards.is_typing_active(current_time)
            is_trackpad = hardware_guards.is_trackpad_active(current_time)
            is_paused = hardware_guards.is_engine_paused()

            if is_typing and not was_typing:
                print(f" ⌨️  [MORSE GUARD] TYPING DETECTED! Engine Muted (1.50s active shield)")
                was_typing = True
            elif not is_typing and was_typing:
                print(f" ✅ [MORSE GUARD] Typing shield expired. Engine listening.")
                was_typing = False

            if is_trackpad and not was_trackpad:
                print(f" 🖱️  [MORSE GUARD] TRACKPAD/SCROLL DETECTED! Engine Muted (1.00s active shield)")
                was_trackpad = True
            elif not is_trackpad and was_trackpad:
                print(f" ✅ [MORSE GUARD] Trackpad shield expired. Engine listening.")
                was_trackpad = False

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n👋 Stopping Hardware Event Guard Diagnostic Suite cleanly...")

if __name__ == "__main__":
    main()
