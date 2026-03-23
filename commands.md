# Activate venv (if not already)
source .venv/bin/activate

# First run — scrapes everything, stores it, sends NO notification
python main.py

# Check what was stored in the DB
sqlite3 tournaments.db "SELECT name, date, location FROM tournaments LIMIT 10;"

# Second run — nothing new, no Telegram message sent
python main.py

