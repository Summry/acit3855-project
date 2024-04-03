import sqlite3
import os

import yaml

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    print("Successfully loaded app config")


def create_db(filename):
    conn = sqlite3.connect(filename)

    c = conn.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS delishery_stats
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            num_of_deliveries INTEGER NOT NULL,
            num_of_schedules INTEGER NOT NULL,
            total_delivery_items INTEGER NOT NULL,
            total_scheduled_deliveries INTEGER NOT NULL,
            last_updated DATETIME NOT NULL)
            ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db(app_config['datastore']['filename'])
