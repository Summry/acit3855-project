import sqlite3
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


def create_db():
    conn = sqlite3.connect(app_config['datastore']['filename'])

    c = conn.cursor()
    c.execute('''
            CREATE TABLE delishery_stats
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            num_of_deliveries INTEGER NOT NULL,
            num_of_schedules INTEGER NOT NULL,
            total_delivery_items INTEGER NOT NULL,
            total_scheduled_deliveries INTEGER NOT NULL,
            last_updated DATETIME NOT NULL)
            ''')
    # last_updated VARCHAR(250) NOT NULL

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
