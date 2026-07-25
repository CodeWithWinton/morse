import time
import threading
import sys

last_keypress_time = 0.0
last_trackpad_time = 0.0
_listener_started = False

def _event_tap_worker():
    global last_keypress_time, last_trackpad_time
    try:
        from Quartz import (
            CGEventTapCreate, kCGSessionEventTap, kCGHeadInsertEventTap,
            kCGEventKeyDown, kCGEventFlagsChanged, kCGEventLeftMouseDown,
            kCGEventRightMouseDown, kCGEventLeftMouseDragged, kCGEventScrollWheel,
            CFRunLoopGetCurrent, CFRunLoopAddSource, CFRunLoopRun,
            kCFAllocatorDefault, kCFRunLoopCommonModes, CGEventTapCreateRunLoopSource
        )
        
        mask = (
            (1 << kCGEventKeyDown) |
            (1 << kCGEventFlagsChanged) |
            (1 << kCGEventLeftMouseDown) |
            (1 << kCGEventRightMouseDown) |
            (1 << kCGEventLeftMouseDragged) |
            (1 << kCGEventScrollWheel)
        )

        def callback(proxy, event_type, event, refcon):
            global last_keypress_time, last_trackpad_time
            now = time.time()
            if event_type in (kCGEventKeyDown, kCGEventFlagsChanged):
                last_keypress_time = now
            elif event_type in (kCGEventLeftMouseDown, kCGEventRightMouseDown, kCGEventLeftMouseDragged, kCGEventScrollWheel):
                last_trackpad_time = now
            return event

        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            0,  # Listen-only / passive event tap
            mask,
            callback,
            None
        )
        
        if tap:
            source = CGEventTapCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            CFRunLoopRun()
    except Exception as e:
        # Graceful fallback if Quartz permissions are limited
        pass

def start_guards():
    """Start background hardware event listener thread."""
    global _listener_started
    if not _listener_started:
        _listener_started = True
        t = threading.Thread(target=_event_tap_worker, daemon=True)
        t.start()

def is_typing_active(current_time=None, window_sec=0.45):
    """Check if a physical keypress occurred within the active typing window."""
    if current_time is None:
        current_time = time.time()
    return (current_time - last_keypress_time) < window_sec

def is_trackpad_active(current_time=None, window_sec=0.40):
    """Check if a trackpad click/drag/scroll occurred within the active trackpad window."""
    if current_time is None:
        current_time = time.time()
    return (current_time - last_trackpad_time) < window_sec

if __name__ == "__main__":
    print("====================================")
    print("   MORSE - Hardware Event Guard Test")
    print("====================================")
    print("🛡️ Starting Quartz CGEventTap listener...")
    start_guards()
    print("Press Ctrl+C to exit. Try typing or clicking your trackpad!\n")
    try:
        while True:
            t_active = is_typing_active()
            m_active = is_trackpad_active()
            status = []
            if t_active: status.append("⌨️ TYPING ACTIVE")
            if m_active: status.append("🖱️ TRACKPAD ACTIVE")
            if status:
                print(f"\r🛡️ Status: {' | '.join(status)}", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Stopped Hardware Event Guard test.")
