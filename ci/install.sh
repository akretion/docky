set -e
sudo apt-get install docker -y
pip install -U -r requirements-build.txt
pip install .
pip freeze
