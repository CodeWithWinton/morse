import time
import ctypes
import ctypes.util

iokit = ctypes.cdll.LoadLibrary(ctypes.util.find_library("IOKit"))
cf = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))

iokit.IOHIDEventSystemClientCreate.restype = ctypes.c_void_p
iokit.IOHIDEventSystemClientCreate.argtypes = [ctypes.c_void_p]

iokit.IOHIDEventSystemClientCopyServices.restype = ctypes.c_void_p
iokit.IOHIDEventSystemClientCopyServices.argtypes = [ctypes.c_void_p]

cf.CFArrayGetCount.restype = ctypes.c_long
cf.CFArrayGetCount.argtypes = [ctypes.c_void_p]

cf.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
cf.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]

iokit.IOHIDServiceClientCopyEvent.restype = ctypes.c_void_p
iokit.IOHIDServiceClientCopyEvent.argtypes = [ctypes.c_void_p, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64]

iokit.IOHIDEventGetFloatValue.restype = ctypes.c_double
iokit.IOHIDEventGetFloatValue.argtypes = [ctypes.c_void_p, ctypes.c_int32]

class ALSSensor:
    def __init__(self):
        self.client = iokit.IOHIDEventSystemClientCreate(None)
        self.services = iokit.IOHIDEventSystemClientCopyServices(self.client) if self.client else None
        self.count = cf.CFArrayGetCount(self.services) if self.services else 0
        self.baseline_lux = 200.0
        
    def read_lux(self):
        if not self.services:
            return 200.0
        kIOHIDEventTypeAmbientLightSensor = 12
        for i in range(self.count):
            service = cf.CFArrayGetValueAtIndex(self.services, i)
            event = iokit.IOHIDServiceClientCopyEvent(service, kIOHIDEventTypeAmbientLightSensor, 0, 0)
            if event:
                lux = iokit.IOHIDEventGetFloatValue(event, (12 << 16) | 0)
                return lux
        return 200.0

    def calibrate(self, seconds=2.0):
        print(f"📊 Calibrating Ambient Light Sensor baseline for {seconds:.1f}s...")
        print("   Keep your hands AWAY from the laptop camera/palm rest...")
        samples = []
        t0 = time.time()
        while time.time() - t0 < seconds:
            samples.append(self.read_lux())
            time.sleep(0.05)
        self.baseline_lux = max(1.0, sum(samples) / len(samples))
        print(f"✅ Baseline Calibrated: {self.baseline_lux:.2f} Lux\n")

if __name__ == "__main__":
    sensor = ALSSensor()
    sensor.calibrate(2.0)
    
    print("💡 Streaming Live Lux & Hand Shadow Proximity Readings...")
    print("Move your hand over the Left Palm Rest vs Right Palm Rest to test shadow depth!\n")
    
    try:
        while True:
            lux = sensor.read_lux()
            ratio = lux / sensor.baseline_lux
            shadow_depth = max(0.0, 1.0 - ratio)
            
            if ratio < 0.85:
                status = f"🖐️ HAND SHADOW DETECTED ({shadow_depth*100:.1f}% shadow)"
            else:
                status = "   Clear"
                
            print(f"  Lux: {lux:6.2f} | Ratio: {ratio:.2f} | Status: {status}")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n👋 Stopping ALS Sensor Monitor...")
