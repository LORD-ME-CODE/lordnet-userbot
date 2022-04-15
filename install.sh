#!/bin/bash
if command -v termux-setup-storage; then
  echo For termux, please use https://raw.githubusercontent.com/LORD-ME-CODE/lordnet-userbot/main/termux-install.sh
  exit 1
fi

if [[ $UID != 0 ]]; then
  echo Please run this script as root
  exit 1
fi

apt update -y
apt install python3 python3-pip git wget gnupg -y || exit 2

su -c "python3 -m pip install -U pip" $SUDO_USER
su -c "python3 -m pip install -U setuptools wheel" $SUDO_USER

if [[ -d "lordnet-userbot" ]]; then
  # shellcheck disable=SC2164
  cd lordnet-userbot
elif [[ -f ".env.dist" ]] && [[ -f "run.py" ]] && [[ -d "modules" ]]; then
  :
else
  git clone https://github.com/LORD-ME-CODE/lordnet-userbot || exit 2
  cd lordnet-userbot || exit 2
fi

if [[ -f ".env.dist" ]] && [[ -f "lordnet.session" ]]; then
  echo "It seems that lordnet-uerbot is already installed. Exiting..."
  exit
fi

su -c "python3 -m pip install -U -r requirements.txt" $SUDO_USER || exit 2

echo
echo "Enter API_ID and API_HASH"
echo "You can get it here -> https://my.telegram.org/apps"
echo "Leave empty to use defaults"
read -r -p "API_ID > " api_id

if [[ $api_id = "" ]]; then
  api_id="5"
  api_hash="1c5c96d5edd401b1ed40db3fb5633e2d"
else
  read -r -p "API_HASH > " api_hash
fi

cat > .env << EOL
API_ID=${api_id}
API_HASH=${api_hash}
EOL

chown -R $SUDO_USER:$SUDO_USER .

echo
echo "Choose installation type:"
echo "[1] PM2"
echo "[2] Systemd service"
echo "[3] Custom (default)"
read -r -p "> " install_type

su -c "python3 install.py ${install_type}" $SUDO_USER || exit 3

case $install_type in
  1)
    if ! command -v pm2; then
      curl -fsSL https://deb.nodesource.com/setup_17.x | bash
      apt install nodejs -y
      npm install pm2 -g
      su -c "pm2 startup" $SUDO_USER
      env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $SUDO_USER --hp /home/$SUDO_USER
    fi
    su -c "pm2 start main.py --name lordnet --interpreter python3" $SUDO_USER
    su -c "pm2 save" $SUDO_USER

    echo "                                      "
    echo "  _               _            _      "
    echo " | | ___  _ __ __| |_ __   ___| |_    "
    echo " | |/ _ \| '__/ _` | '_ \ / _ | __|   "
    echo " | | (_) | | | (_| | | | |  __| |_    "
    echo " |_|\___/|_|  \__,_|_|_|_|\___|\___   "
    echo "  _   _ ___  ___ _ __| |__   ___ | |_ "
    echo "| | | / __|/ _ | '__| '_ \ / _ \| __| "
    echo "| |_| \__ |  __| |  | |_) | (_) | |_  "
    echo " \__,_|___/\___|_|  |_.__/ \___/ \__|  "
    echo "                                      "
    echo "Great! lordnet-userbot installed successfully and running now!"
    echo "Installation type: PM2"
    echo "Start with: \"pm2 start lordnet\""
    echo "Stop with: \"pm2 stop lordnet\""
    echo "Process name: lordnet"
    echo "============================"
    ;;
  2)
    cat > /etc/systemd/system/lordnet.service << EOL
[Unit]
Description=Service for lordnet userbot
[Service]
Type=simple
ExecStart=$(which python3) ${PWD}/run.py
WorkingDirectory=${PWD}
Restart=always
User=${SUDO_USER}
Group=${SUDO_USER}
[Install]
WantedBy=multi-user.target
EOL
    systemctl daemon-reload
    systemctl start lordnet
    systemctl enable lordnet

    echo "                                      "
    echo "  _               _            _      "
    echo " | | ___  _ __ __| |_ __   ___| |_    "
    echo " | |/ _ \| '__/ _` | '_ \ / _ | __|   "
    echo " | | (_) | | | (_| | | | |  __| |_    "
    echo " |_|\___/|_|  \__,_|_|_|_|\___|\___   "
    echo "  _   _ ___  ___ _ __| |__   ___ | |_ "
    echo "| | | / __|/ _ | '__| '_ \ / _ \| __| "
    echo "| |_| \__ |  __| |  | |_) | (_) | |_  "
    echo " \__,_|___/\___|_|  |_.__/ \___/ \__|  "
    echo "                                      "
    echo "Great! lordnet-userbot installed successfully and running now!"
    echo "Installation type: Systemd service"
    echo "Start with: \"sudo systemctl start lordnet\""
    echo "Stop with: \"sudo systemctl stop lordnet\""
    echo "============================"
    ;;
  *)
    echo "                                      "
    echo "  _               _            _      "
    echo " | | ___  _ __ __| |_ __   ___| |_    "
    echo " | |/ _ \| '__/ _` | '_ \ / _ | __|   "
    echo " | | (_) | | | (_| | | | |  __| |_    "
    echo " |_|\___/|_|  \__,_|_|_|_|\___|\___   "
    echo "  _   _ ___  ___ _ __| |__   ___ | |_ "
    echo "| | | / __|/ _ | '__| '_ \ / _ \| __| "
    echo "| |_| \__ |  __| |  | |_) | (_) | |_  "
    echo " \__,_|___/\___|_|  |_.__/ \___/ \__|  "
    echo "                                      "
    echo "Great! lordnet-userbot installed successfully!"
    echo "Installation type: Custom"
    echo "Start with: \"python3 run.py\""
    echo "============================"
    ;;
esac

chown -R $SUDO_USER:$SUDO_USER .
