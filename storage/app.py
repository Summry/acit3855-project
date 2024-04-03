import datetime
import json
import os
import logging
import logging.config
import time
from threading import Thread

import connexion
import yaml
from base import Base
from connexion import NoContent
from models import Delivery, Schedule
from pykafka import KafkaClient
from pykafka.common import OffsetType
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker

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

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Config File:", app_conf_file)
logger.info("Log Config File:", log_conf_file)

def configure_app():
    """Stores log events in the app.log file for every request

    Returns:
        Dictionary: app configuration details
    """
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
    return app_config

app_config = configure_app()

def configure_logging():
    """Logging configuration - creates app.log file
    """
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

configure_logging()
logger = logging.getLogger('basicLogger')

# Database Credential Constants
db_creds = app_config['datastore']
DB_USER = db_creds['user']
DB_PASSWORD = db_creds['password']
DB_HOST = db_creds['hostname']
DB_PORT = db_creds['port']
DB_NAME = db_creds['db']

connected_to_db = False

while not connected_to_db:
    try:
        logger.info(f"Connecting to Database... Hostname: {DB_HOST}, Port: {DB_PORT}")

        DB_ENGINE = create_engine(
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}", pool_pre_ping=True, pool_size=20, pool_recycle=300)
        Base.metadata.bind = DB_ENGINE
        DB_SESSION = sessionmaker(bind=DB_ENGINE)

        connected_to_db = True
        logger.info(f"Successfully connected to the MySQL DB. Hostname: {DB_HOST}, Port: {DB_PORT}")
    except:
        logger.error("Failed to connect to DB. Retrying in 5 seconds...")
        time.sleep(app_config['datastore']['retry_interval'])

def log_post_info(event, trace_id):
    """Logs requests

    Args:
        event (string): event type
        trace_id (string): event tracer
    """
    # logger = logging.getLogger('basicLogger')
    logger.info(f"Stored event {event} request with a trace id of {trace_id}")


def log_get_info(event, start_timestamp, len_of_results):
    """Logs GET requests for each event

    Args:
        event (string): Delivery or Schedule
        start_timestamp (string): Datetime URL query parameter
        len_of_results (int): length of the results list
    """
    # logger = logging.getLogger('basicLogger')
    logger.info(
        f"Query for {event} after {start_timestamp} returns {len_of_results} results")

connected_to_kafka = False

while not connected_to_kafka:
    try:
        hostname = "%s:%d" % (app_config['events']['hostname'], app_config['events']['port'])
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config['events']['topic'])]

        consumer = topic.get_simple_consumer(
            consumer_group=b'event_group',
            reset_offset_on_start=False,
            auto_offset_reset=OffsetType.LATEST
        )

        connected_to_kafka = True
        logger.info("Successfully connected to Kafka. Hostname: %s, Port: %d" % (app_config['events']['hostname'], app_config['events']['port']))
    except:
        logger.error("Failed to connect to Kafka. Retrying in 5 seconds...")
        time.sleep(app_config['events']['retry_interval'])

def write_to_database(message):
    """This function will write the body/data/payload to the database

    Args:
        Kafka Message (dict): message obtained from kafka
    """

    session = DB_SESSION()

    evt = {}
    body = message['payload']

    if message['type'] == "delivery":
        evt = Delivery(
            delivery_id=body['delivery_id'],
            user_id=body['user_id'],
            item_quantity=body['item_quantity'],
            trace_id=body['trace_id']
        )

    elif message['type'] == "schedule":
        evt = Schedule(
            schedule_id=body['schedule_id'],
            user_id=body['user_id'],
            number_of_deliveries=body['number_of_deliveries'],
            trace_id=body['trace_id']
        )

    session.add(evt)

    session.commit()
    session.close()

    log_post_info(message['type'], body['trace_id'])


def get_deliveries(start_timestamp, end_timestamp):
    """GET request that gets list of deliveries

    Args:
        start_timestamp (string): lower boundary of timestampts
        end_timestamp (string): upper boundary of timestamps

    Returns:
        JSON: json array of items
    """
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(
        start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(
        end_timestamp, "%Y-%m-%d %H:%M:%S")

    results = session.query(Delivery).filter(
        and_(
            Delivery.requested_date > start_timestamp_datetime,
            Delivery.requested_date <= end_timestamp_datetime
        )
    ).all()

    results_list = []

    for result in results:
        results_list.append(result.to_dict())

    session.close()

    log_get_info('deliveries', start_timestamp, len(results_list))

    return results_list, 200


def get_schedules(start_timestamp, end_timestamp):
    """GET request that gets list of schedules

    Args:
        start_timestamp (string): URL query parameter
        end_timestamp (string): URL query parameter
    """
    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(
        start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.datetime.strptime(
        end_timestamp, "%Y-%m-%d %H:%M:%S")

    results = session.query(Schedule).filter(
        and_(
            Schedule.created_date > start_timestamp_datetime,
            Schedule.created_date <= end_timestamp_datetime
        )
    ).all()

    results_list = []

    for result in results:
        results_list.append(result.to_dict())

    session.close()

    log_get_info('schedules', start_timestamp, len(results_list))

    return results_list, 200


def process_messages():
    """ Process event messages """

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)

        logger.info("Message: %s" % msg)

        write_to_database(msg)

        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("delishery.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    # configure_logging()

    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])
