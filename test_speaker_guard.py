import ctypes
import ctypes.util
import time

coreaudio = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreAudio"))

kAudioObjectSystemObject = 1
kAudioHardwarePropertyDefaultOutputDevice = 0x644F7574 # 'dOut'
kAudioDevicePropertyDeviceIsRunningSomewhere = 0x676F6E65 # 'gone'
kAudioObjectPropertyScopeGlobal = 1735159650          # 'glob'
kAudioObjectPropertyElementMain = 0

class AudioObjectPropertyAddress(ctypes.Structure):
    _fields_ = [
        ("mSelector", ctypes.c_uint32),
        ("mScope", ctypes.c_uint32),
        ("mElement", ctypes.c_uint32),
    ]

def is_built_in_speaker_active():
    # 1. Get Default Output Device
    addr = AudioObjectPropertyAddress(
        mSelector=kAudioHardwarePropertyDefaultOutputDevice,
        mScope=kAudioObjectPropertyScopeGlobal,
        mElement=kAudioObjectPropertyElementMain
    )
    device_id = ctypes.c_uint32()
    size = ctypes.c_uint32(ctypes.sizeof(device_id))
    
    status = coreaudio.AudioObjectGetPropertyData(
        kAudioObjectSystemObject,
        ctypes.byref(addr),
        0,
        None,
        ctypes.byref(size),
        ctypes.byref(device_id)
    )
    if status != 0:
        return False
        
    # 2. Check if output device is currently playing audio
    run_addr = AudioObjectPropertyAddress(
        mSelector=kAudioDevicePropertyDeviceIsRunningSomewhere,
        mScope=kAudioObjectPropertyScopeGlobal,
        mElement=kAudioObjectPropertyElementMain
    )
    is_running = ctypes.c_uint32()
    run_size = ctypes.c_uint32(ctypes.sizeof(is_running))
    
    status = coreaudio.AudioObjectGetPropertyData(
        device_id.value,
        ctypes.byref(run_addr),
        0,
        None,
        ctypes.byref(run_size),
        ctypes.byref(is_running)
    )
    return is_running.value != 0

def main():
    print("==========================================================================")
    print("      MORSE - macOS Zero-CPU Speaker Audio Playing Guard Inspection       ")
    print("==========================================================================")
    print("Play music or audio out of your speakers to test detection...\n")
    
    for i in range(20):
        active = is_built_in_speaker_active()
        status = "🔊 SPEAKER AUDIO PLAYING (MORSE PAUSED)" if active else "🟢 Speakers Quiet (MORSE ACTIVE)"
        print(f"  [{i+1:02d}/20] Status: {status}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
