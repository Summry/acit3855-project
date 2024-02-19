import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
  app_config = yaml.safe_load(f.read())['datastore']

db_conn = mysql.connector.connect(
  host=app_config['hostname'],
  user=app_config['user'],
  password=app_config['password'],
  database=app_config['db']
)

db_cursor = db_conn.cursor()

db_cursor.execute('''
                  CREATE TABLE delivery_report
                  (id INT NOT NULL AUTO_INCREMENT,
                  delivery_id VARCHAR(250) NOT NULL,
                  user_id VARCHAR(250) NOT NULL,
                  item_quantity INTEGER NOT NULL,
                  requested_date DATETIME NOT NULL,
                  trace_id VARCHAR(250) NOT NULL,
                  CONSTRAINT delivery_pk PRIMARY KEY (id)
                  )
                  ''')

db_cursor.execute('''
                  CREATE TABLE schedule_report
                  (id INT NOT NULL AUTO_INCREMENT,
                  schedule_id VARCHAR(250) NOT NULL,
                  user_id VARCHAR(250) NOT NULL,
                  number_of_deliveries INTEGER NOT NULL,
                  created_date DATETIME NOT NULL,
                  trace_id VARCHAR(250) NOT NULL,
                  CONSTRAINT schedule_pk PRIMARY KEY (id)
                  )
                  ''')

db_conn.commit()
db_conn.close()
