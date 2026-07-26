import time
import threading
import sys

last_keypress_time = 0.0
last_trackpad_time = 0.0
_listener_started = False
engine_paused = False
_last_fn_press_time = 0.0

def _event_tap_worker():
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
                
                # Check for Fn key (keycode 63 OR kCGEventFlagMaskSecondaryFn 0x800000)
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
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            0,  # Listen-only / passive event tap
            mask,
            callback,
            None
        )
        
        if tap:
            source = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            print("🛡️  [Quartz Guard] Keyboard & Trackpad event listener ACTIVE!")
            CFRunLoopRun()
        else:
            print("\n⚠️  [Quartz Warning] CGEventTap failed to initialize. Enable Terminal in System Settings -> Privacy & Security -> Accessibility for keyboard suppression.")
    except Exception as e:
        print(f"\n⚠️  [Quartz Warning] CGEventTap Error: {e}")

def start_guards():
    """Start background hardware event listener thread."""
    global _listener_started
    if not _listener_started:
        _listener_started = True
        t = threading.Thread(target=_event_tap_worker, daemon=True)
        t.start()

def is_engine_paused():
    """Check if MORSE engine is currently paused by Fn key toggle."""
    return engine_paused

def is_typing_active(current_time=None, window_sec=1.50):
    """Check if a physical keypress occurred within the active typing window (increased to 1.50s)."""
    if current_time is None:
        current_time = time.time()
    return (current_time - last_keypress_time) < window_sec

def is_trackpad_active(current_time=None, window_sec=1.00):
    """Check if a trackpad click/drag/scroll occurred within active window (1.00s)."""
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
