#!/bin/bash
# This installs dependencies for Ybyrá in Ubuntu and updates Ybyra
#
chmod 765 ybyra_apo.py
chmod 765 ybyra_sa.py
if [ -d ~/bin ]; then
  echo "Copying YBYRA scripts to ~/bin"
  cp ybyra_*.py ~/bin/
else
  echo "You do not have ~/bin"
  echo "Run YBYRA locally using ./ybyra_sa.py for intance"
fi
pip3 install svgwrite
sudo apt install python3-tk
