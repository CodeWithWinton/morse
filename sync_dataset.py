#!/usr/bin/env python3
"""
MORSE TLM 1.5 — Universal Hugging Face Dataset Sync Launcher
Usage: python3 sync_dataset.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data_tools.hf_dataset_sync import run_sync_menu

if __name__ == "__main__":
    run_sync_menu()
