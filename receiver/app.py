import datetime
import json
import logging
import logging.config
import time
import uuid

import connexion
import yaml
from connexion import NoContent
from pykafka import KafkaClient


def configure_app():
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
    return app_config


app_config = configure_app()

# time.sleep(15)


def configure_logging():
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)


def log_info(event, trace_id, status_code=None):
    logger = logging.getLogger('basicLogger')
    if status_code:
        logger.info(
            f"Returned event {event} response {trace_id} with status {status_code}")
    else:
        logger.info(
            f"Received event {event} request with a trace of {trace_id}")


def create_kafka_producer():
    max_retries = app_config['events']['max_retries']
    retry_interval = app_config['events']['retry_interval']
    retry_count = 0
    logger = logging.getLogger('basicLogger')

    while retry_count < max_retries:
        try:
            client = KafkaClient(
                hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
            topic = client.topics[str.encode(app_config['events']['topic'])]
            producer = topic.get_sync_producer()
            return producer

        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            logger.info(
                f"Retrying to connect to Kafka. Retry count: {retry_count}")
            time.sleep(retry_interval)
            retry_count += 1

    logger.error(
        f"Failed to connect to Kafka after {max_retries} retries. Exiting now.")
    return None


kafka_producer = create_kafka_producer()


def invoke_kafka_producer(event_type, body):
    """Connects with Kafka and sends a message

    Args:
        event_type (string): Name of the event being received (delivery or schedule)
        body (object): Payload or request body of the event
    """

    if kafka_producer:
        msg = {
            "type": event_type,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "payload": body
        }
        msg_str = json.dumps(msg)
        kafka_producer.produce(msg_str.encode('utf-8'))
    else:
        logger = logging.getLogger('basicLogger')
        logger.error("No producer found, exiting now.")


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
app.add_api("delishery.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    configure_logging()

    app.run(port=app_config['app']['port'], host=app_config['app']['host'])