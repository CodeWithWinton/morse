#!/usr/bin/env python3
"""
MORSE TLM 1.5 — Universal Data Collection Launcher
Usage: python3 collect_data.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data_tools.universal_collector import run_interactive_collector

if __name__ == "__main__":
    run_interactive_collector()
