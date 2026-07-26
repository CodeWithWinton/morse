#import <AppKit/AppKit.h>

void fire_haptic_native(NSInteger pattern) {
    @autoreleasepool {
        id performer = [NSHapticFeedbackManager defaultPerformer];
        if (performer) {
            [performer performFeedbackPattern:(NSHapticFeedbackPattern)pattern
                               performanceTime:NSHapticFeedbackPerformanceTimeDefault];
        }
    }
}
