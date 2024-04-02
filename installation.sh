sudo apt update
sudo apt upgrade

sudo apt install wget git python3 python3-venv python3.8-venv python3-pip
bash <(wget -qO- https://raw.githubusercontent.com/AUTOMATIC1111/stable-diffusion-webui/master/webui.sh)

curl -X GET http://127.0.0.1:7860/sdapi/v1/sd-models