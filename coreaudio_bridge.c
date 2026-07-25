#include <CoreAudio/CoreAudio.h>
#include <stdio.h>
#include <stdlib.h>

// Function to get the default input device AudioObjectID
AudioObjectID get_default_input_device(void) {
    AudioObjectID deviceID = kAudioObjectUnknown;
    AudioObjectPropertyAddress propertyAddress = {
        kAudioHardwarePropertyDefaultInputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    UInt32 dataSize = sizeof(deviceID);
    OSStatus status = AudioObjectGetPropertyData(
        kAudioObjectSystemObject,
        &propertyAddress,
        0,
        NULL,
        &dataSize,
        &deviceID
    );
    if (status != noErr) {
        return kAudioObjectUnknown;
    }
    return deviceID;
}

// Function to query input streams and total discrete channels directly from macOS HAL
int query_input_channels(AudioObjectID deviceID) {
    if (deviceID == kAudioObjectUnknown) {
        deviceID = get_default_input_device();
    }
    if (deviceID == kAudioObjectUnknown) {
        return -1;
    }

    AudioObjectPropertyAddress propertyAddress = {
        kAudioDevicePropertyStreamConfiguration,
        kAudioDevicePropertyScopeInput,
        kAudioObjectPropertyElementMain
    };

    UInt32 dataSize = 0;
    OSStatus status = AudioObjectGetPropertyDataSize(
        deviceID,
        &propertyAddress,
        0,
        NULL,
        &dataSize
    );
    if (status != noErr || dataSize == 0) {
        return -1;
    }

    AudioBufferList *bufferList = (AudioBufferList *)malloc(dataSize);
    if (!bufferList) return -1;

    status = AudioObjectGetPropertyData(
        deviceID,
        &propertyAddress,
        0,
        NULL,
        &dataSize,
        bufferList
    );

    int totalChannels = 0;
    if (status == noErr) {
        printf("🎙️ [CoreAudio HAL] Probing AudioObjectID %u:\n", deviceID);
        printf("   • Input Streams Count: %u\n", bufferList->mNumberBuffers);
        for (UInt32 i = 0; i < bufferList->mNumberBuffers; i++) {
            printf("   • Stream #%u: %u Channels\n", i + 1, bufferList->mBuffers[i].mNumberChannels);
            totalChannels += bufferList->mBuffers[i].mNumberChannels;
        }
        printf("   • Total HAL Input Channels: %d\n", totalChannels);
    }

    free(bufferList);
    return totalChannels;
}
