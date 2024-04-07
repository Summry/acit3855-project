import datetime
import json
import os
import logging
import logging.config
import time
import uuid

import connexion
import yaml
from connexion import NoContent
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
            hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
        topic = client.topics[str.encode(app_config['events']['topic'])]
        producer = topic.get_sync_producer()
        connected_to_kafka = True
    except:
        logger.error("Failed to connect to Kafka, retrying in 5 seconds...")
        time.sleep(app_config['events']['retry_interval'])


logger.info("Connected to Kafka!")


def log_info(event, trace_id, status_code=None):
    logger = logging.getLogger('basicLogger')
    if status_code:
        logger.info(
            f"Returned event {event} response {trace_id} with status {status_code}")
    else:
        logger.info(
            f"Received event {event} request with a trace of {trace_id}")


def invoke_kafka_producer(event_type, body):
    """Connects with Kafka and sends a message

    Args:
        event_type (string): Name of the event being received (delivery or schedule)
        body (object): Payload or request body of the event
    """

    msg = {
        "type": event_type,
        "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": body
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


def add_delishery_delivery(body):
    """
    This endpoint will add a new delivery.
    """

    trace_id = str(uuid.uuid4())
    log_info('DELIVERY', trace_id)
    body["trace_id"] = trace_id

    # response = requests.post(app_config['deliverystore']['url'], json=body)
    invoke_kafka_producer('delivery', body)

    log_info('DELIVERY', trace_id, 201)

    return NoContent, 201


def add_delishery_schedule(body):
    """
    This endpoint will add a new schedule.
    """

    trace_id = str(uuid.uuid4())
    log_info('SCHEDULE', trace_id)
    body['trace_id'] = trace_id

    # response = requests.post(app_config['schedulestore']['url'], json=body)
    invoke_kafka_producer('schedule', body)

    log_info('SCHEDULE', trace_id, 201)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("delishery.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])
