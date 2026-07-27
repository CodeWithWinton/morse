---
annotations_creators:
- no-annotation
language:
- en
license:
- mit
multilinguality:
- monolingual
size_categories:
- 1k-10k
source_datasets:
- original
task_categories:
- audio-classification
task_ids:
- audio-intent-classification
- keyword-spotting
pretty_name: MacBook Unibody Acoustic Kinetic Tap Dataset (TLM 1.0)
dataset_info:
  features:
  - name: audio
    dtype: audio
  - name: label
    dtype:
      class_label:
        names:
        - double_left_palm
        - double_right_palm
        - noise_and_typing
  splits:
  - name: train
    num_bytes: 226492416
    num_examples: 2600
---

# 🎙️ MacBook Unibody Acoustic Kinetic Tap Dataset (TLM 1.0)

## Dataset Description
This dataset contains **2,600 raw 48.0kHz 350ms floating-point NumPy (`.npy`) audio windows** capturing physical kinetic impulse waves traveling across a metallic MacBook unibody aluminum chassis.

It was engineered for **MORSE**, a software-defined acoustic AI engine powered by **TLM 1.0 (Tap Learning Model)**.

- **Repository:** [https://github.com/CodeWithWinton/morse](https://github.com/CodeWithWinton/morse)
- **Paper / Model:** TLM 1.0 (Tap Learning Model)
- **Author:** Manas Maheshwari ([@CodeWithWinton](https://github.com/CodeWithWinton))

## Dataset Structure
* **`double_left_palm/`** (800 `.npy` samples): Double-taps on the left metal palm rest.
* **`double_right_palm/`** (800 `.npy` samples): Double-taps on the right metal palm rest (30cm away from built-in mic across aluminum deck).
* **`noise_and_typing/`** (1,000 `.npy` samples): Multi-surface ambient noise, typing clacks, desk taps, and 200 hard negative earphone lid snaps & pen clicks.

## Physical Feature Highlights
* **50ms Mechanical Wave Dispersion Ratio:** Measures physical kinetic energy ring-down across aluminum decks (0.160 - 0.330 chassis tap vs 0.039 - 0.115 air click).
* **Bass Energy Ratio (120 - 600 Hz):** Captures unibody structural resonance near built-in microphone.

## Citation
```bibtex
@misc{maheshwari2026morse,
  author = {Manas Maheshwari},
  title = {MORSE: Software-Defined Acoustic Tap Engine for Metallic Unibody Laptops},
  year = {2026},
  publisher = {GitHub / Hugging Face},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/CodeWithWinton/morse}}
}
```
