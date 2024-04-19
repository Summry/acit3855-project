import datetime
import uuid
import json
import os
import logging
import logging.config
import time

import connexion
import yaml
from base import Base
from threading import Thread
from connexion.middleware import MiddlewarePosition
from create_database import create_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from anomaly import Anomaly
from pykafka import KafkaClient
from pykafka.common import OffsetType

time.sleep(10)

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

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

logger.info(f"Delivery Anomaly Threshold Value: Greater Than {app_config['events']['delivery_anomaly']} Item Quantity")
logger.info(f"Schedule Anomaly Threshold Value: Less Than {app_config['events']['schedule_anomaly']} Number of Deliveries")


connected_to_kafka = False

while not connected_to_kafka:
    try:
        hostname = "%s:%d" % (app_config['events']['hostname'], app_config['events']['port'])
        client = KafkaClient(hosts=hostname)
        events_topic = client.topics[str.encode(app_config['events']['topic'])]

        consumer = events_topic.get_simple_consumer(
            consumer_group=b'event_group',
            reset_offset_on_start=False,
            auto_offset_reset=OffsetType.LATEST
        )

        connected_to_kafka = True
        logger.info("Successfully connected to Kafka. Hostname: %s, Port: %d" % (app_config['events']['hostname'], app_config['events']['port']))
    except:
        logger.error("Failed to connect to Kafka. Retrying in 5 seconds...")
        time.sleep(app_config['events']['retry_interval'])


DB_ENGINE = create_engine("sqlite:///%s" % app_config['datastore']['filename'])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

create_db(app_config['datastore']['filename'])

logger.info("Successfully created DB Engine and Database table: %s - Database table anomaly has been created." % app_config['datastore']['filename'])


def write_to_database(msg):
    """This function will write the ANOMALY body/data/payload to the database

    Args:
        Kafka Message (dict): message obtained from kafka
    """
    
    logger.info("Writing Anomaly to the SQLite database...")
    
    payload = msg['payload']
    
    session = DB_SESSION()
    
    new_anomaly = Anomaly(
        event_id=str(uuid.uuid4()),
        trace_id=payload['trace_id'],
        event_type=msg['type'],
        anomaly_type='TooHigh' if msg['type'] == 'delivery' else 'TooLow',
        description=f"Anomaly detected for {msg['type']} event with {f"{payload['item_quantity']} delivery items which is TOO HIGH!" if msg['type'] == 'delivery' else f"{payload['number_of_deliveries']} number of deliveries which is TOO LOW!"}"
    )
    
    session.add(new_anomaly)
    
    session.commit()
    session.close()
    
    logger.info("Successfully written the Anomaly to the SQLite database!")


def get_anomalies(anomaly_type): # anomaly_type: str is a query parameter in the url path (TooHigh || TooLow)
    logger.info(f"Received GET /anomalies request with anomaly_type: {anomaly_type}")
    
    results = []
    
    session = DB_SESSION()
    
    anomalies = session.query(Anomaly).filter(Anomaly.anomaly_type.lower() == anomaly_type.lower()).all().reverse().limit(1)
    
    [results.append(anomaly.to_dict()) for anomaly in anomalies]
    
    if not anomalies:
        logger.error(f"No anomalies found with the anomaly_type: {anomaly_type} in the SQLite database. Anomalies: {results}")
        return {'message': 'Anomalies not found'}, 404
    
    logger.info(f"Anomalies found with the anomaly_type: {anomaly_type} in the SQLite database. Anomalies: {results}")
    
    return results, 200


def detect_anomalies():
    """This function will detect anomalies"""
    
    logger.info("Started periodic anomaly detection of messages from Kafka")

    for kafka_msg in consumer:
        msg_str = kafka_msg.value.decode('utf-8')
        msg = json.loads(msg_str)
    
        if msg['type'] == 'delivery':
            if msg['payload']['item_quantity'] > app_config['events']['delivery_anomaly']:
                write_to_database(msg)
                
        if msg['type'] == 'schedule':
            if msg['payload']['number_of_deliveries'] < app_config['events']['schedule_anomaly']:
                write_to_database(msg)
        
        consumer.commit_offsets()
        logger.info(f"Successfully processed Anomaly: {msg}")


def check_db_exists():
    """Check if the SQLite database exists

    Returns:
        bool: True if the database exists, False otherwise
    """
    try:
        session = DB_SESSION()
        session.close()
        return True
    except:
        return False


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("delishery.yaml", base_path="/anomaly_detector", strict_validation=True, validate_responses=True)

if __name__ == "__main__":

    if not check_db_exists():
        create_db(app_config['datastore']['filename'])
        
    t1 = Thread(target=detect_anomalies)
    t1.daemon = True
    t1.start()

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])
