import sqlite3

import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


def drop_table():
    conn = sqlite3.connect(app_config['datastore']['filename'])

    c = conn.cursor()
    c.execute('''
            DROP TABLE delishery_stats
            ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    drop_table()
