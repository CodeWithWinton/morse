import ctypes
import ctypes.util

# Load CoreAudio and CoreFoundation
coreaudio = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreAudio"))
cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))

# CoreAudio HAL constants
kAudioObjectSystemObject = 1
kAudioHardwarePropertyDefaultInputDevice = 0x64496E20 # 'dIn '
kAudioDevicePropertyStreamConfiguration = 0x736C7374  # 'slst'
kAudioObjectPropertyScopeGlobal = 1735159650          # 'glob'
kAudioObjectPropertyScopeInput = 1768843636           # 'inpt'
kAudioObjectPropertyElementMain = 0

class AudioObjectPropertyAddress(ctypes.Structure):
    _fields_ = [
        ("mSelector", ctypes.c_uint32),
        ("mScope", ctypes.c_uint32),
        ("mElement", ctypes.c_uint32),
    ]

class AudioBuffer(ctypes.Structure):
    _fields_ = [
        ("mNumberChannels", ctypes.c_uint32),
        ("mDataByteSize", ctypes.c_uint32),
        ("mData", ctypes.c_void_p),
    ]

class AudioBufferList(ctypes.Structure):
    _fields_ = [
        ("mNumberBuffers", ctypes.c_uint32),
        ("mBuffers", AudioBuffer * 1),
    ]

def main():
    print("==========================================================================")
    print("      MORSE - macOS CoreAudio HAL Low-Level Hardware Mic Inspection       ")
    print("==========================================================================")
    
    # 1. Get Default Input Device ID
    addr = AudioObjectPropertyAddress(
        mSelector=kAudioHardwarePropertyDefaultInputDevice,
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
        print(f"❌ Failed to get default input device. Status: {status}")
        return
        
    print(f"🎙️ Default Input Device ID: {device_id.value}")
    
    # 2. Query Raw Hardware Stream Configuration (Channel Count)
    stream_addr = AudioObjectPropertyAddress(
        mSelector=kAudioDevicePropertyStreamConfiguration,
        mScope=kAudioObjectPropertyScopeInput,
        mElement=kAudioObjectPropertyElementMain
    )
    
    buf_size = ctypes.c_uint32()
    status = coreaudio.AudioObjectGetPropertyDataSize(
        device_id.value,
        ctypes.byref(stream_addr),
        0,
        None,
        ctypes.byref(buf_size)
    )
    
    if status != 0:
        print(f"❌ Failed to get stream config size. Status: {status}")
        return
        
    print(f"  HAL Stream Config Size: {buf_size.value} bytes")
    
    buffer_data = (ctypes.c_uint8 * buf_size.value)()
    status = coreaudio.AudioObjectGetPropertyData(
        device_id.value,
        ctypes.byref(stream_addr),
        0,
        None,
        ctypes.byref(buf_size),
        ctypes.byref(buffer_data)
    )
    
    buf_list = ctypes.cast(buffer_data, ctypes.POINTER(AudioBufferList)).contents
    print(f"  Number of Raw HAL Audio Buffers: {buf_list.mNumberBuffers}")
    
    total_channels = 0
    for i in range(buf_list.mNumberBuffers):
        ch = buf_list.mBuffers[i].mNumberChannels
        total_channels += ch
        print(f"  Buffer #{i+1}: {ch} Channels")
        
    print(f"\n📊 TOTAL LOW-LEVEL HARDWARE CHANNELS EXPOSED BY KERNEL: {total_channels}")

if __name__ == "__main__":
    main()
