sudo yum install python3 python3-pip awscli -y && \
python3 -m venv venv --prompt kochi && \
. venv/bin/activate && \
pip3 install wheel && \
pip3 install -r requirements.txt && \
curl https://cli-assets.heroku.com/install.sh | sudo sh