# Trip booking class

class FlightBooker:
  def __init__(self):
    print("flight booking constructor")
  
  def getTripOptions(self, date, source , dest):
    print(f"search Flight options for: date {date}, from: {source}, to: {dest}")


if __name__ == "__main__":
  tripBooker = FlightBooker()
  tripBooker.getTripOptions("20200416", "Boston", "Delhi")

# export FlightBooker
        