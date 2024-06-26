import json
import logging
import logging.config
import os
import time
from datetime import datetime

import connexion
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from base import Base
from connexion.middleware import MiddlewarePosition
from create_database import create_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from stats import Stats
from pykafka import KafkaClient


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

time.sleep(10)

connected_to_kafka = False

while not connected_to_kafka:
    try:
        client = KafkaClient(
            hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}"
        )

        event_log_topic = client.topics[str.encode(app_config['events']['log_topic'])]
        event_log_producer = event_log_topic.get_sync_producer()

        connected_to_kafka = True
        logger.info("Successfully connected to Kafka. Hostname: %s, Port: %d" % (app_config['events']['hostname'], app_config['events']['port']))
    except:
        logger.error("Failed to connect to Kafka, retrying in 5 seconds...")
        time.sleep(app_config['events']['retry_interval'])


def produce_service_event_log():
    """
    This function produces a log message to the event log topic.
    """

    ready_message = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": {
            "code": "0003",
            "message": "Processor Service is running!"
        }
    }

    ready_message_str = json.dumps(ready_message)
    event_log_producer.produce(ready_message_str.encode('utf-8'))


DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

create_db(app_config['datastore']['filename'])

def log_get_info(event, event_list):
    """Logs GET requests for each event

    Args:
        event (string): name of the event (deliveries or schedules)
        event_list (list): list of the events
    """
    logger = logging.getLogger('basicLogger')
    logger.info(
        f"NUMBER OF NEW {event} EVENTS RECEIVED DURING THIS INTERVAL...........: \n{len(event_list)}\n")


def log_get_debug(event, trace_id=None, stats=None):
    """Logs GET requests debugs for each event

    Args:
        event (string): name of the event (deliveries or schedules)
        trace_id (string): trace id of the event
        stats (dictionary): stats of the event
    """
    logger = logging.getLogger('basicLogger')
    if trace_id:
        logger.debug(
            f"{event} EVENT WITH TRACE ID {trace_id} HAS BEEN PROCESSED")
    if stats:
        logger.debug(
            f"UPDATED {event} STATISTICS........................................: \n{stats}\n")


def log_get_error(event):
    """Logs GET requests errors for each event

    Args:
        event (string): name of the event (deliveries or schedules)
    """
    logger = logging.getLogger('basicLogger')
    logger.error(
        f"NO {event} FOUND - COULDN'T FIND {event} - NOT 200 CODE IT'S SOMETHING ELSE")


def write_to_database(data):
    """Writes to the SQLite database

    Args:
        data (dictionary): data to be written to the database
    """

    session = DB_SESSION()

    new_stat = Stats(
        num_of_deliveries=data['num_of_deliveries'],
        num_of_schedules=data['num_of_schedules'],
        total_delivery_items=data['total_delivery_items'],
        total_scheduled_deliveries=data['total_scheduled_deliveries'],
        last_updated=data['last_updated']
    )

    session.add(new_stat)

    session.commit()
    session.close()


def read_from_database():
    """Reads from the SQLite database

    Returns:
        dictionary: current stats from the database
          - num_of_deliveries (int): number of deliveries
          - num_of_schedules (int): number of schedules
          - total_delivery_items (int): total delivery items
          - total_scheduled_deliveries (int): total scheduled deliveries
          - last_updated (datetime): last updated timestamp
    """

    session = DB_SESSION()

    current_stats = session.query(Stats).order_by(
        Stats.last_updated.desc()).first()

    if not current_stats:

        current_stats = {
            'num_of_deliveries': 0,
            'num_of_schedules': 0,
            'total_delivery_items': 0,
            'total_scheduled_deliveries': 0,
            'last_updated': datetime(1970, 1, 1, 0, 0, 0)
        }
    else:
        current_stats = current_stats.to_dict()

    session.close()

    return current_stats


def process_data(current_stats, deliveries, schedules, curr_date):
    """Processes the statistical numeric data to be written to the database

    Args:
        current_stats (dictionary): currently-read stats from the database
        deliveries (list): list of deliveries events
        schedules (list): list of schedules events
        curr_date (datetime): current date and time

    Returns:
        dictionary: new stats to be written to the database
        - num_of_deliveries (int): number of deliveries
        - num_of_schedules (int): number of schedules
        - total_delivery_items (int): total delivery items
        - total_scheduled_deliveries (int): total scheduled deliveries
    """

    total_delivery_items = current_stats['total_delivery_items']
    total_scheduled_deliveries = current_stats['total_scheduled_deliveries']

    num_of_deliveries = current_stats['num_of_deliveries'] + len(deliveries)
    num_of_schedules = current_stats['num_of_schedules'] + len(schedules)

    for delivery in deliveries:

        log_get_debug("DELIVERIES", trace_id=delivery['trace_id'])
        total_delivery_items += delivery['item_quantity']

    for schedule in schedules:

        log_get_debug("SCHEDULES", trace_id=schedule['trace_id'])
        total_scheduled_deliveries += schedule['number_of_deliveries']

    updated_stats = {
        "num_of_deliveries": num_of_deliveries,
        "num_of_schedules":  num_of_schedules,
        "total_delivery_items": total_delivery_items,
        "total_scheduled_deliveries": total_scheduled_deliveries,
        "last_updated": curr_date
    }

    log_get_debug("DELIVERIES", stats={
        "num_of_deliveries": updated_stats['num_of_deliveries'],
        "total_delivery_items": updated_stats['total_delivery_items']
    })
    log_get_debug("SCHEDULES", stats={
        "num_of_schedules": updated_stats['num_of_schedules'],
        "total_scheduled_deliveries": updated_stats['total_scheduled_deliveries']
    })

    return updated_stats


def get_new_data(event, last_updated, curr_date):
    """Gets new data from the MySQL database

    Args:
        event (string): name of the event (deliveries or schedules)
        last_updated (string): last updated timestamp
        curr_date (string): current date and time

    Returns:
        Response: response objet from the MySQL database
        - json: json array of items (use the .json() method to get the data as a list of dictionaries)
        - status_code: status code of the response (use the .status_code attribute to get the status code as an integer)
    """
    return requests.get(f"{app_config[f'{event}store']['url']}", params={
        "start_timestamp": last_updated,
        "end_timestamp": curr_date
    }, timeout=10)


def produce_event_log(message):
    msg = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": {
            "code": "0004",
            "message": message
        }
    }
    msg_str = json.dumps(msg)
    event_log_producer.produce(msg_str.encode('utf-8'))


def populate_stats():
    """Periodically processes the statistical numeric data
    """
    logger = logging.getLogger('basicLogger')
    logger.info(
        "AYE BROOO - PERIODIC PROCESSING HAS STARTED............................................................")

    current_stats = read_from_database()

    last_updated = datetime.strftime(
        current_stats['last_updated'], "%Y-%m-%d %H:%M:%S")
    curr_date_datetime = datetime.now()
    curr_date_string = datetime.strftime(
        curr_date_datetime, "%Y-%m-%d %H:%M:%S")

    deliveries = get_new_data('delivery', last_updated, curr_date_string)
    schedules = get_new_data('schedule', last_updated, curr_date_string)

    log_get_info("DELIVERIES", deliveries.json())
    if deliveries.status_code != 200:
        log_get_error("DELIVERIES")
    log_get_info("SCHEDULES", schedules.json())
    if schedules.status_code != 200:
        log_get_error("SCHEDULES")

    num_configurable_messages = len(deliveries.json()) + len(schedules.json())
    if num_configurable_messages > app_config['events']['threshold']:
        produce_event_log(f"Received more than {app_config['events']['threshold']} configurable events/messages ({num_configurable_messages} messages received).")
        logger.info("Logging [0004]... Received more than 25 configurable events/messages successfully!")

    new_stats = process_data(
        current_stats, deliveries.json(), schedules.json(), curr_date_datetime)

    write_to_database(new_stats)

    logger.info(
        "AYE BROOO - PERIODIC PROCESSING HAS ENDED..............................................................")


def get_stats():
    """Gets the current stats from the SQLite database

    Returns:
        dictionary: current stats from the database
        - num_of_deliveries (int): number of deliveries
        - num_of_schedules (int): number of schedules
        - total_delivery_items (int): total delivery items
        - total_scheduled_deliveries (int): total scheduled deliveries
        - last_updated (datetime): last updated timestamp
    """
    logger = logging.getLogger('basicLogger')
    logger.info(
        "REQUESTING CURRENT API STATISTICS...................................................................")

    current_stats = read_from_database()

    if not current_stats:
        return logger.error("NO CURRENT API STATISTICS FOUND..........................................................."), 404

    new_dict = {
        "num_of_deliveries": current_stats['num_of_deliveries'],
        "num_of_schedules": current_stats['num_of_schedules'],
        "total_delivery_items": current_stats['total_delivery_items'],
        "total_scheduled_deliveries": current_stats['total_scheduled_deliveries'],
    }

    logger.debug(
        f"CURRENT API STATISTICS.........................................................: \n{new_dict}\n")

    logger.info(
        "CURRENT API STATISTICS REQUEST HAS BEEN COMPLETED...................................................")

    return new_dict, 200


def init_scheduler():
    """Initializes the periodic scheduler
    """
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


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
app.add_api("delishery.yaml", base_path="/processor", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    produce_service_event_log()

    if not check_db_exists():
        create_db(app_config['datastore']['filename'])

    init_scheduler()

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])
