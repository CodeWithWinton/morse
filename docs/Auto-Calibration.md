# Auto-Calibration

The **Auto-Calibration Wizard** (`morse calibrate`) guarantees that [[Morse - Master Hub]] works plug-and-play on any laptop model in any room environment.

## Why Calibration Is Essential
Different laptop models (MacBook Air, MacBook Pro, Dell XPS, Lenovo ThinkPad) have:
* Different microphone sensitivity gains.
* Different body materials (aluminum, magnesium alloy, plastic).
* Different room background noise floors (AC, fans, loud TV).

## The Wizard Workflow

```
[ morse calibrate ]
        │
        ▼
Step 1: Ambient Noise Floor Measurement (3 Seconds)
        - Listens to background room noise without tapping.
        - Calculates baseline noise volume (e.g. Vol = 11.0).
        │
        ▼
Step 2: Physical Tap Capture (Prompt: "Tap chassis 3 times!")
        - Measures laptop's specific aluminum resonant frequency ratio.
        - Calculates peak volume & Crest Factor.
        │
        ▼
Step 3: Auto-Generate `config.json`
        - Writes personalized thresholds to user's config file.
```

## Generated `config.json` Schema
```json
{
  "device_model": "MacBookAir10,1",
  "calibrated_thresholds": {
    "volume_gate": 15.0,
    "ratio_threshold": 3.2,
    "crest_factor_min": 2.3,
    "decay_ratio_max": 0.45
  },
  "actions": {
    "single_tap": "mute_system_audio",
    "double_tap": "toggle_spotify_play_pause",
    "triple_tap": "launch_raycast"
  }
}
```

See [[Architecture]] for where calibration fits in the overall system.

Back to [[Morse - Master Hub]]
