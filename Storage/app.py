import connexion, yaml, logging, logging.config, datetime
from connexion import NoContent

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from models import Delivery, Schedule

def configure_app():
  """Stores log events in the app.log file for every request

  Returns:
      Dictionary: app configuration details
  """
  with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
  return app_config

app_config = configure_app()

# Database Credential Constants
db_creds = app_config['datastore']
DB_USER = db_creds['user']
DB_PASSWORD = db_creds['password']
DB_HOST = db_creds['hostname']
DB_PORT = db_creds['port']
DB_NAME = db_creds['db']

DB_ENGINE = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}", pool_pre_ping=True)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def configure_logging():
  """Logging configuration - creates app.log file
  """
  with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

def log_db_info():
  """Logs database connection details
  """
  logger = logging.getLogger('basicLogger')
  logger.info(f"Connecting to DB. Hostname:{DB_HOST}, Port:{DB_PORT}")

def log_post_info(event, trace_id):
  """Logs requests

  Args:
      event (string): event type
      trace_id (string): event tracer
  """
  logger = logging.getLogger('basicLogger')
  logger.info(f"Stored event {event} request with a trace id of {trace_id}")

def log_get_info(event, start_timestamp, len_of_results):
  """Logs GET requests for each event

  Args:
      event (string): Delivery or Schedule
      start_timestamp (string): Datetime URL query parameter
      len_of_results (int): length of the results list
  """
  logger = logging.getLogger('basicLogger')
  logger.info(f"Query for {event} after {start_timestamp} returns {len_of_results} results")

def add_delishery_delivery(body):
  """
  This endpoint will add a new delivery.
  """

  session = DB_SESSION()

  log_db_info()

  dlv = Delivery(
    delivery_id = body['delivery_id'],
    user_id = body['user_id'],
    item_quantity = body['item_quantity'],
    trace_id = body['trace_id']
  )

  session.add(dlv)

  session.commit()
  session.close()

  log_post_info('delivery', body['trace_id'])

  return NoContent, 201

def add_delishery_schedule(body):
  """
  This endpoint will add a new schedule.
  """

  session = DB_SESSION()

  log_db_info()

  sch = Schedule(
    schedule_id = body['schedule_id'],
    user_id = body['user_id'],
    number_of_deliveries = body['number_of_deliveries'],
    trace_id = body['trace_id']
  )

  session.add(sch)

  session.commit()
  session.close()

  log_post_info('schedule', body['trace_id'])

  return NoContent, 201

def get_deliveries(start_timestamp, end_timestamp):
  """GET request that gets list of deliveries

  Args:
      start_timestamp (string): lower boundary of timestampts
      end_timestamp (string): upper boundary of timestamps

  Returns:
      JSON: json array of items
  """
  session = DB_SESSION()

  start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
  end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")

  results = session.query(Delivery).filter(
    and_(
      Delivery.requested_date > start_timestamp_datetime,
      Delivery.requested_date <= end_timestamp_datetime
    )
  ).all()

  results_list = []

  for result in results:
    results_list.append(result.to_dict())
  print("RESULTS LIST.......................................................\n", results_list)

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

  start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S")
  end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S")

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

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("delishery.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  configure_logging()

  app.run(port=app_config['app']['port'])