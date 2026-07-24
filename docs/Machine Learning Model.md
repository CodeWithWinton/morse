# Machine Learning Model

The entire success of [[Morse - Master Hub]] relies on this single component: **Noise Filtering**.

## The Problem (False Positives)
If a user taps the laptop, it creates a vibration spike. If a user aggressively hits the `Spacebar` while typing an essay, it *also* creates a vibration spike. 

## The Solution
Instead of a simple magnitude threshold, we will treat this as a Time-Series Classification problem.

### Data Collection
1. Record 1,000 deliberate chassis taps.
2. Record 10 minutes of heavy typing and trackpad usage.
3. Export raw X,Y,Z waveform data to a `.csv`.

### Feature Engineering
We will extract features from the 800Hz waveform:
* **Peak Width (Duration):** Taps are usually shorter (50ms) than heavy typing impacts.
* **Frequency Analysis:** Taps on aluminum sound/feel different than taps on plastic keys.

### Model Selection
* **Random Forest / XGBoost:** Lightweight enough to run in the background without draining MacBook battery life.
* **Scikit-Learn:** Used for training the model locally.
