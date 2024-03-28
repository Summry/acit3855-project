import json
import logging
import logging.config

import connexion
import yaml
from connexion.middleware import MiddlewarePosition
from pykafka import KafkaClient
from starlette.middleware.cors import CORSMiddleware


def configure_app():
    with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
    return app_config


app_config = configure_app()

# time.sleep(15)

# hostname = "%s:%d" % (app_config['events']['hostname'],
#                       app_config['events']['port'])
# client = KafkaClient(hosts=hostname)
# topic = client.topics[str.encode(app_config['events']['topic'])]


def configure_logging():
    with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)


def get_delivery_report(index):
    """Get delivery reading in History

    Args:
        index (string): Index of the message queue
    """

    hostname = "%s:%d" % (app_config['events']['hostname'],
                          app_config['events']['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

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
    hostname = "%s:%d" % (app_config['events']['hostname'],
                          app_config['events']['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

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
app.add_api("delishery.yaml", strict_validation=True, validate_responses=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    configure_logging()

    app.run(port=app_config['app']['port'], host='0.0.0.0')
