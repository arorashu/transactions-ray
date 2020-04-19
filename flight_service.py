# Trip booking class

import ray
import time
import json

@ray.remote
class FlightBooker:
  def __init__(self):
    print("flight booking constructor")
    
    with open("./flight_db.json") as f:
      self.flight_db = json.load(f)

    # list of dict
    # print(type(self.flight_db))
  
  # @ray.remote spans a new process (new pid), anything that you print here
  # does not show on the console, unless you do a ray.get() on the calling process
  # 

  def getTripOptions(self, date, source , dest):
    print(f"search Flight options for: date {date}, from: {source}, to: {dest}")
    flight_db = self.flight_db
    
    res = []
    for flight_option in flight_db:
      if flight_option['from'] == source and flight_option['to'] == dest and flight_option['date'] == date:
        res.append(flight_option)

    return res


if __name__ == "__main__":
  tripBooker = FlightBooker()
  tripBooker.getTripOptions("20200416", "Boston", "Delhi")

