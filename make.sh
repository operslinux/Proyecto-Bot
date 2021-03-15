echo '[!] Updating...'
apt-get update > install.log
echo
echo '[!] Installing Dependencies...'
echo '    Python3'
apt-get -y install python3 python3-pip &>> install.log
echo
pip install telegram &>> install.log
echo
pip install img &>> install.log
echo
pip install qrcode &>> install.log
echo
echo '[!] Setting Permissions...'
chmod +x LaHackerBot.py
echo
echo '[!] Installed.'