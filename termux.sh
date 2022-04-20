if ! command -v termux-setup-storage; then
  echo This script can be executed only on Termux
  exit 1
fi

termux-wake-lock

apt update -y
apt install python3 git clang wget libjpeg-turbo libcrypt ndk-sysroot zlib -y || exit 2
pkg install opencv-python

python3 -m pip install -U pip
LDFLAGS="-L${PREFIX}/lib/" CFLAGS="-I${PREFIX}/include/" pip3 install --upgrade wheel pillow
pip3 uninstall pyrogram

if [[ -d "lordnet-userbot" ]]; then
  cd lordnet-userbot
elif [[ -f ".env.dist" ]] && [[ -f "run.py" ]] && [[ -d "modules" ]]; then
  :
else
  git clone https://github.com/LORD-ME-CODE/lordnet-userbot || exit 2
  cd lordnet-userbot || exit 2
fi

if [[ -f ".env" ]] && [[ -f "lordnet.session" ]]; then
  echo "It seems that lordnet-userbot is already installed. Exiting..."
  exit
fi

python3 -m pip install -U -r requirements.txt || exit 2

echo
echo "Enter API_ID and API_HASH"
echo "You can get it here -> https://my.telegram.org/apps"
echo "Leave empty to use defaults"
read -r -p "API_ID > " api_id

if [[ $api_id = "" ]]; then
  api_id="14895435"
  api_hash="e8205235cc85f4d3b9b8733a24954950"
else
  read -r -p "API_HASH > " api_hash
fi

cat > .env << EOL
API_ID=${api_id}
API_HASH=${api_hash}
EOL

python3 install.py 3 || exit 3

echo
echo "============================"
echo "Great! lordnet-userbot installed successfully!"
echo "Start with: \"python3 run.py\""
echo "============================"
