#import <AppKit/AppKit.h>
#import <AudioToolbox/AudioToolbox.h>

void fire_haptic_native(NSInteger pattern) {
    @autoreleasepool {
        // Initialize NSApplication connection so AppKit delivers trackpad haptic events
        [NSApplication sharedApplication];
        
        id performer = [NSHapticFeedbackManager defaultPerformer];
        if (performer) {
            [performer performFeedbackPattern:(NSHapticFeedbackPattern)pattern
                               performanceTime:NSHapticFeedbackPerformanceTimeDefault];
        }
        
        // Also trigger CoreAudio Trackpad Haptic System Sound ID 1521
        AudioServicesPlaySystemSound(1521);
    }
}
