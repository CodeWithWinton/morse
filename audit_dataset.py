#!/usr/bin/env python3
"""
MORSE TLM 1.5 — Master Dataset Health & Label Auditor Launcher
Usage: python3 audit_dataset.py [dataset_directory]
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data_tools.audit_incoming_data import audit_dataset_directory

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "dataset_double_taps"
    audit_dataset_directory(target_dir)
