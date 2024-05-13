apt update && apt install -y python3 python3-venv libpq-dev postgresql-client gcc python3-dev
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export SOURCE_DB=postgresql://$DB_USER:$DB_PASSWORD@$DB_ENDPOINT/$DB_NAME
psql $SOURCE_DB -f scripts/oltp_init.sql
python3 download.py
python3 populate.py
