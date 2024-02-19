import connexion, requests, yaml, logging, uuid, logging.config
from connexion import NoContent

def configure_app():
  with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
  return app_config

app_config = configure_app()

def configure_logging():
  with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

def log_info(event, trace_id, status_code=None):
  logger = logging.getLogger('basicLogger')
  if status_code:
    logger.info(f"Returned event {event} response {trace_id} with status {status_code}")
  else:
    logger.info(f"Received event {event} request with a trace of {trace_id}")

def add_delishery_delivery(body):
  """
  This endpoint will add a new delivery.
  """

  # update_events_file("deliveries", event_message)
  trace_id = str(uuid.uuid4())
  log_info('DELIVERY', trace_id)
  body["trace_id"] = trace_id

  response = requests.post(app_config['deliverystore']['url'], json=body)
  log_info('DELIVERY', trace_id, response.status_code)

  return NoContent, response.status_code

def add_delishery_schedule(body):
  """
  This endpoint will add a new schedule.
  """
  
  # update_events_file("schedules", event_message)
  trace_id = str(uuid.uuid4())
  log_info('SCHEDULE', trace_id)
  body['trace_id'] = trace_id

  with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
  
  response = requests.post(app_config['schedulestore']['url'], json=body)
  log_info('SCHEDULE', trace_id, response.status_code)

  return NoContent, response.status_code

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("delishery.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  configure_logging()
  
  app.run(port=app_config['app']['port'])