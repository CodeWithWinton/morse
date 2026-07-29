"""
MORSE TLM 1.5 — Universal Cross-Platform Hardware Guards
=========================================================
macOS: Quartz CGEventTap (keyboard, trackpad, Fn toggle, speaker detection)
Windows/Linux: Graceful no-op fallback (guards disabled, DSP + ML still protect)
"""
import time
import threading
import sys
import platform

PLATFORM = platform.system()

last_keypress_time = 0.0
last_trackpad_time = 0.0
_listener_started = False
engine_paused = False
_last_fn_press_time = 0.0


def _event_tap_worker_macos():
    """macOS-only Quartz CGEventTap listener."""
    global last_keypress_time, last_trackpad_time, engine_paused, _last_fn_press_time
    try:
        from Quartz import (
            CGEventTapCreate, kCGSessionEventTap, kCGHeadInsertEventTap,
            kCGEventKeyDown, kCGEventFlagsChanged,
            kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventLeftMouseDragged,
            kCGEventRightMouseDown, kCGEventRightMouseUp, kCGEventRightMouseDragged,
            kCGEventMouseMoved, kCGEventOtherMouseDown, kCGEventOtherMouseUp, kCGEventOtherMouseDragged,
            kCGEventScrollWheel, CFRunLoopGetCurrent, CFRunLoopAddSource, CFRunLoopRun,
            kCFAllocatorDefault, kCFRunLoopCommonModes, CFMachPortCreateRunLoopSource,
            CGEventGetIntegerValueField, kCGKeyboardEventKeycode
        )

        mask = (
            (1 << kCGEventKeyDown) |
            (1 << kCGEventFlagsChanged) |
            (1 << kCGEventLeftMouseDown) |
            (1 << kCGEventLeftMouseUp) |
            (1 << kCGEventRightMouseDown) |
            (1 << kCGEventRightMouseUp) |
            (1 << kCGEventMouseMoved) |
            (1 << kCGEventLeftMouseDragged) |
            (1 << kCGEventRightMouseDragged) |
            (1 << kCGEventOtherMouseDown) |
            (1 << kCGEventOtherMouseUp) |
            (1 << kCGEventOtherMouseDragged) |
            (1 << kCGEventScrollWheel)
        )

        def callback(proxy, event_type, event, refcon):
            global last_keypress_time, last_trackpad_time, engine_paused, _last_fn_press_time
            now = time.time()

            if event_type == kCGEventFlagsChanged:
                from Quartz import CGEventGetFlags
                flags = CGEventGetFlags(event)
                keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
                is_fn_event = (keycode == 63) or bool(flags & 0x00800000)
                if is_fn_event and (now - _last_fn_press_time) > 0.35:
                    _last_fn_press_time = now
                    engine_paused = not engine_paused
                    if engine_paused:
                        print("\n🔴 MORSE ENGINE PAUSED (Fn Toggle) - Muted")
                    else:
                        print("\n🟢 MORSE ENGINE RESUMED (Fn Toggle) - Listening")

            if event_type in (kCGEventKeyDown, kCGEventFlagsChanged):
                last_keypress_time = now
            elif event_type in (
                kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventRightMouseDown, kCGEventRightMouseUp,
                kCGEventMouseMoved, kCGEventLeftMouseDragged, kCGEventRightMouseDragged,
                kCGEventOtherMouseDown, kCGEventOtherMouseUp, kCGEventOtherMouseDragged, kCGEventScrollWheel
            ):
                last_trackpad_time = now
            return event

        tap = CGEventTapCreate(
            kCGSessionEventTap, kCGHeadInsertEventTap, 0, mask, callback, None
        )

        if tap:
            source = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            print("🛡️  [Quartz Guard] Keyboard & Trackpad event listener ACTIVE!")
            CFRunLoopRun()
        else:
            print("\n⚠️  [Quartz Warning] CGEventTap failed. Enable Terminal in Privacy & Security -> Accessibility.")
    except Exception as e:
        print(f"\n⚠️  [Quartz Warning] CGEventTap Error: {e}")


def start_guards():
    """Start background hardware event listener thread (macOS only, no-op on other platforms)."""
    global _listener_started
    if _listener_started:
        return
    _listener_started = True

    if PLATFORM == "Darwin":
        t = threading.Thread(target=_event_tap_worker_macos, daemon=True)
        t.start()
    else:
        # ponytail: Windows/Linux keyboard guard not implemented yet.
        # DSP 4-Pillar Shield + 82% ML confidence floor still protect against false positives.
        print("🛡️  [Hardware Guard] Keyboard/Trackpad guard not available on this platform (DSP + ML guards active)")


def is_engine_paused():
    return engine_paused


def is_typing_active(current_time=None, window_sec=1.50):
    if current_time is None:
        current_time = time.time()
    return (current_time - last_keypress_time) < window_sec


def is_trackpad_active(current_time=None, window_sec=1.00):
    if current_time is None:
        current_time = time.time()
    return (current_time - last_trackpad_time) < window_sec


_speaker_active_cache = False
_last_speaker_check_time = 0.0


def is_speaker_output_active():
    """Check if speakers are playing audio. macOS only; returns False on other platforms."""
    global _speaker_active_cache, _last_speaker_check_time
    now = time.time()
    if (now - _last_speaker_check_time) < 0.5:
        return _speaker_active_cache

    _last_speaker_check_time = now

    if PLATFORM != "Darwin":
        _speaker_active_cache = False
        return False

    try:
        import subprocess
        res = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"],
                             capture_output=True, text=True, timeout=0.08)
        if res.returncode == 0:
            vol = int(res.stdout.strip())
            if vol == 0:
                _speaker_active_cache = False
                return False
        res_apps = subprocess.run(["pgrep", "-x", "Music|Spotify|com.apple.audio.ComponentResult"],
                                  capture_output=True, text=True, timeout=0.08)
        _speaker_active_cache = (res_apps.returncode == 0)
    except Exception:
        _speaker_active_cache = False

    return _speaker_active_cache


if __name__ == "__main__":
    print("====================================")
    print("   MORSE - Hardware Event Guard Test")
    print("====================================")
    print(f"🖥️ Platform: {PLATFORM}")
    start_guards()
    print("Press Ctrl+C to exit.\n")
    try:
        while True:
            status = []
            if is_typing_active(): status.append("⌨️ TYPING")
            if is_trackpad_active(): status.append("🖱️ TRACKPAD")
            if status:
                print(f"\r🛡️ {' | '.join(status)}", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Stopped.")
