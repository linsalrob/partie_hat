"""
Train a random forest on our known organisms and use that to classify unknown data
"""

import os
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-f', help='')
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()