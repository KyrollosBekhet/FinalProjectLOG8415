sudo apt-get update;
sudo apt install python3-pip
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install pymysql
pip install paramiko
pip install sshtunnel