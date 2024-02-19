import connexion, json, os
from datetime import datetime
from connexion import NoContent
from constants import EVENT_FILE, APP_PORT, MAX_RECENT_EVENTS

def check_and_create_file():
  """
  Check if the events.json file exists.
  If it does not, create it and initialize it.
  """

  if os.path.exists(f"./${EVENT_FILE}"):
    return
  else:
    initialize_events = {
      "num_deliveries": 0,
      "recent_deliveries": [],
      "num_schedules": 0,
      "recent_schedules": []
    }
    with open(EVENT_FILE, 'w', encoding='utf-8') as fp:
      json.dump(initialize_events, fp, indent=2)

def read_events_file():
  """
  This function reads the json data from events.json file and returns it.
  """

  with open(EVENT_FILE, 'r', encoding='utf-8') as events_file:
    events_data = json.load(events_file)
  return events_data

def update_events_file(event_type, event_message):
  """
  This function will update the events.json file according
  to the endpoint that is getting hit.
  """

  num_event = f"num_{event_type}"
  recent_event = f"recent_{event_type}"

  event_data = read_events_file()

  event_data[num_event] += 1
  if len(event_data[recent_event]) >= MAX_RECENT_EVENTS:
    event_data[recent_event].pop()
    event_data[recent_event] = [event_message] + event_data[recent_event]
  else:
    event_data[recent_event] = [event_message] + event_data[recent_event]

  with open(EVENT_FILE, 'w', encoding='utf-8', buffering=8192) as events_json_file:
    json.dump(event_data, events_json_file, indent=2, ensure_ascii=False)
    events_json_file.truncate() # https://stackoverflow.com/questions/62498864/python-writing-to-json-file-adds-extra-brackets
    events_json_file.write("\n")

def add_delishery_delivery(body):
  """
  This endpoint will add a new delivery.
  """

  delivery_id, user_id, item_quantity, _ = body.values()
  parsed_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
  event_message = {
    "msg_data": f"User {user_id} requested a delivery with {item_quantity} items.",
    "received_timestamp": parsed_datetime
  }

  update_events_file("deliveries", event_message)

  return NoContent, 201

def add_delishery_schedule(body):
  """
  This endpoint will add a new schedule.
  """
  
  schedule_id, user_id, num_of_deliveries, _ = body.values()
  parsed_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
  event_message = {
    "msg_data": f"User {user_id} requested a schedule with {num_of_deliveries} deliveries.",
    "received_timestamp": parsed_datetime
  }

  update_events_file("schedules", event_message)

  return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("delishery.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  check_and_create_file()
  
  app.run(port=APP_PORT)