import datetime
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
from eventstats import EventStats
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


connected_to_kafka = False

while not connected_to_kafka:
    try:
        hostname = "%s:%d" % (app_config['events']['hostname'], app_config['events']['port'])
        client = KafkaClient(hosts=hostname)
        events_topic = client.topics[str.encode(app_config['events']['log_topic'])]

        consumer = events_topic.get_simple_consumer(
            consumer_group=b'log_group',
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

logger.info("Successfully created DB Engine and Database table: %s - Database table event_log_stats has been created." % app_config['datastore']['filename'])


def write_to_database(msg):
    """This function will write the body/data/payload to the database

    Args:
        Kafka Message (dict): message obtained from kafka
    """
    
    payload = msg['payload']
    
    session = DB_SESSION()
    
    new_event = EventStats(
        message=payload['message'],
        code=payload['code']
    )
    
    logger.debug("Writing to the SQLite database...: %s" % new_event.to_dict())
    
    session.add(new_event)
    session.commit()
    
    logger.info("Successfully written to the SQLite database: %s" % new_event.to_dict())
    
    session.close()


def get_event_stats():
    """GET endpoint to get all the event log stats from the SQLite database.

    Returns:
        dict: object containing the event log stats
        - 0001: Number of times Receiver service started
        - 0002: Number of times Storage service started
        - 0003: Number of times Processor serviec started
        - 0004: Number of times the number of messages over 25 were received.
    """
    
    session = DB_SESSION()
    
    logger.info("Querying the database for event log stats")
    
    event_stats = session.query(EventStats).all()
    
    output_stats = {
        "0001": 0,
        "0002": 0,
        "0003": 0,
        "0004": 0
    }
    
    if event_stats:
        for event in event_stats:
            output_stats[event.code] += 1

    return output_stats, 200


def process_messages():
    """This function will process the messages from Kafka"""
    
    logger.info("Started periodic processing of messages from Kafka")
    try:
        for kafka_msg in consumer:
            msg_str = kafka_msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            write_to_database(msg)
            consumer.commit_offsets()
            logger.debug("Message processed: %s" % msg_str)
    except:
        logger.error("Periodic processing - Failed to process message from Kafka.")


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
app.add_api("delishery.yaml", base_path="/event_logger", strict_validation=True, validate_responses=True)

if __name__ == "__main__":

    if not check_db_exists():
        create_db(app_config['datastore']['filename'])
        
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])
