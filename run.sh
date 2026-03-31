#!/bin/bash

# 1. Sequential Execution (Wait for each to finish)
echo "Setting resolution..."
wlr-randr --output NOOP-1 --custom-mode 1920x1080

echo "Setting usb..."
./new_usb_gadget_setup.sh

echo "Running kvm..."
python kvm.py