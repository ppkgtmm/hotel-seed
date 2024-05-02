python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
psql $SOURCE_DB -f scripts/oltp_init.sql
python3 download.py
python3 populate.py
