import json
import logging
import logging.config
import time
import os

import connexion
import yaml
from connexion.middleware import MiddlewarePosition
from pykafka import KafkaClient
from starlette.middleware.cors import CORSMiddleware

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


time.sleep(15)

connected_to_kafka = False

while not connected_to_kafka:
    try:
        hostname = "%s:%d" % (app_config['events']['hostname'],
                      app_config['events']['port'])
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config['events']['topic'])]
        connected_to_kafka = True
    except:
        logger.error("Failed to connect to Kafka, retrying in 5 seconds...")
        time.sleep(app_config['events']['retry_interval'])


logger.info("Connected to Kafka!")


def get_delivery_report(index):
    """Get delivery reading in History

    Args:
        index (string): Index of the message queue
    """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger = logging.getLogger('basicLogger')
    logger.info('Retrieving DELIVERY at index %d', index)
    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'delivery':
                if count == index:
                    return msg['payload'], 200
                count += 1

    except:
        logger.error("No more messages found.")

    logger.error("Could not find DELIVERY at index %d" % index)
    return {'message': "NOT FOUND"}, 404


def get_schedule_report(index):
    """Get schedule reading in History

    Args:
        index (int): Index of the event history

    Returns:
        Event Object: Event object and the corresponding status code
    """
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger = logging.getLogger('basicLogger')
    logger.info('Retrieving SCHEDULE at index %d', index)
    try:
        count = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'schedule':
                if count == index:
                    return msg['payload'], 200
                count += 1

    except:
        logger.error("No more messages found.")

    logger.error("Could not find SCHEDULE at index %d" % index)
    return {'message': "NOT FOUND"}, 404


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
app.add_api("delishery.yaml", base_path="/audit", strict_validation=True, validate_responses=True)

if __name__ == "__main__":

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])
