# Trip booking class

import ray

from flight_service import FlightBooker

class TripBooker:
  def __init__(self):
    print("trip booking constructor")
  
  def getTripOptions(self, date, source , dest):
    print(f"search Trip options for: date {date}, from: {source}, to:{dest}")


if __name__ == "__main__":
  ray.init()
  tripBooker = TripBooker()
  tripBooker.getTripOptions("20200430", "BOS", "DEL")
  flightBooker = FlightBooker.remote()
  # flightBooker = FlightBooker()
  # flightBooker.getTripOptions("20200430", "BOS", "DEL")
  res = flightBooker.getTripOptions.remote("20200430", "BOS", "DEL")
  resolvedResult = ray.get(res)
  print("resolvedResult: " + str(resolvedResult))

