import uuid
import csv

"""
The purpose of this file is to help Apache JMeter 
generate random uuids for the following API properties:
  - delivery_id
  - schedule_id
  - user_id
"""

with open('deliveries.csv', 'w', newline='') as fp:
    write_csv = csv.DictWriter(fp, fieldnames=['delivery_id', 'user_id'])
    write_csv.writeheader()
    for i in range(1000):
        write_csv.writerow({
            "delivery_id": uuid.uuid4(),
            "user_id": uuid.uuid4()
        })

with open('schedules.csv', 'w', newline='') as fp:
    write_csv = csv.DictWriter(fp, fieldnames=['schedule_id', 'user_id'])
    write_csv.writeheader()
    for i in range(1000):
        write_csv.writerow({
            "schedule_id": uuid.uuid4(),
            "user_id": uuid.uuid4()
        })
