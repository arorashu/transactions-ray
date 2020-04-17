# Trip booking class

from flight_service import FlightBooker

class TripBooker:
  def __init__(self):
    print("trip booking constructor")
  
  def getTripOptions(self, date, source , dest):
    print(f"search trip options for: date {date}, from: {source}, to:{dest}")


if __name__ == "__main__":
  tripBooker = TripBooker()
  tripBooker.getTripOptions("20200416", "Boston", "Delhi")
  flightBooker = FlightBooker()
  flightBooker.getTripOptions("20200416", "Boston", "Delhi")

        