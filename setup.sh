#!/bin/sh
echo 'Starting Monitor Lizard Setup'
sudo apt-get update
sudo apt-get install tshark
sudo apt-get install libnotify-bin

while read lib ; do 
    pip install $lib
done < requirements.txt

echo 'export SSLKEYLOGFILE=~/.ssl-key.log' >> ~/.bashrc 
exec bash