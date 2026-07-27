#import <AVFoundation/AVFoundation.h>
#import <Foundation/Foundation.h>
#import <Accelerate/Accelerate.h>

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        printf("====================================\n");
        printf("   MORSE - Native Apple VPIO Engine \n");
        printf("====================================\n");
        
        AVAudioEngine *engine = [[AVAudioEngine alloc] init];
        AVAudioInputNode *inputNode = [engine inputNode];
        
        NSError *error = nil;
        BOOL success = [inputNode setVoiceProcessingEnabled:YES error:&error];
        if (success) {
            printf("🍏 Apple VoiceProcessingIO Hardware AEC Enabled Successfully!\n");
        } else {
            printf("❌ VPIO Error: %s\n", error ? [[error localizedDescription] UTF8String] : "Unknown");
        }
        
        AVAudioFormat *format = [inputNode inputFormatForBus:0];
        printf("🎙️ Hardware Format: %.0f Hz | %u Channels\n", format.sampleRate, format.channelCount);
        
        [inputNode installTapOnBus:0 bufferSize:2048 format:format block:^(AVAudioPCMBuffer * _Nonnull buffer, AVAudioTime * _Nonnull when) {
            float *channelData = buffer.floatChannelData[0];
            vDSP_Length frameLength = buffer.frameLength;
            
            float rms = 0.0;
            vDSP_rmsqv(channelData, 1, &rms, frameLength);
            float vol = rms * 100.0;
            
            if (vol > 3.0) {
                printf("⚡ [VPIO Hardware Mic Event] Vol: %.2f\n", vol);
            }
        }];
        
        [engine startAndReturnError:&error];
        printf("🔴 Listening via Native Apple Hardware VPIO! Press Ctrl+C to stop.\n\n");
        [[NSRunLoop currentRunLoop] run];
    }
    return 0;
}
