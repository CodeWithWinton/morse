#include <AudioToolbox/AudioToolbox.h>
#include <stdio.h>

static AudioUnit g_vpio_unit = NULL;

int enable_vpio(int sample_rate) {
    AudioComponentDescription desc;
    desc.componentType = kAudioUnitType_Output;
    desc.componentSubType = kAudioUnitSubType_VoiceProcessingIO;
    desc.componentManufacturer = kAudioUnitManufacturer_Apple;
    desc.componentFlags = 0;
    desc.componentFlagsMask = 0;
    
    AudioComponent comp = AudioComponentFindNext(NULL, &desc);
    if (!comp) return -1;
    
    OSStatus status = AudioComponentInstanceNew(comp, &g_vpio_unit);
    if (status != noErr) return -2;
    
    // Enable Input Scope
    UInt32 enableIO = 1;
    status = AudioUnitSetProperty(
        g_vpio_unit,
        kAudioOutputUnitProperty_EnableIO,
        kAudioUnitScope_Input,
        1, // Input bus
        &enableIO,
        sizeof(enableIO)
    );
    
    // Enable VoiceProcessing AEC (Bypass = 0)
    UInt32 bypass = 0;
    AudioUnitSetProperty(
        g_vpio_unit,
        kAUVoiceIOProperty_BypassVoiceProcessing,
        kAudioUnitScope_Global,
        0,
        &bypass,
        sizeof(bypass)
    );
    
    status = AudioUnitInitialize(g_vpio_unit);
    if (status != noErr) return -3;
    
    status = AudioOutputUnitStart(g_vpio_unit);
    if (status != noErr) return -4;
    
    return 0; // Success! VPIO Hardware AEC Active
}

void disable_vpio(void) {
    if (g_vpio_unit) {
        AudioOutputUnitStop(g_vpio_unit);
        AudioUnitUninitialize(g_vpio_unit);
        AudioComponentInstanceDispose(g_vpio_unit);
        g_vpio_unit = NULL;
    }
}
