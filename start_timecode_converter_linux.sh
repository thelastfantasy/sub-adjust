#!/bin/sh

echo "Running timecode_converter.py..."
nohup python3 timecode_converter.py &> /dev/null &
