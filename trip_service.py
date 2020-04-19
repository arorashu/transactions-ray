# Trip booking class

import ray
from flight_service import FlightBooker
from car_service import CarBooker


class TripBooker:
    def __init__(self):
        # print("trip booking constructor")
        pass

    def get_trip_options(self, date, source, dest):
        print(f"search Trip options for: date {date}, from: {source}, to:{dest}")


if __name__ == "__main__":
    ray.init()
    date = "20200430"
    source = "BOS"
    destination = "DEL"
    tripBooker = TripBooker()
    tripBooker.get_trip_options(date, source, destination)
    flight_booker = FlightBooker.remote()
    flight_options = flight_booker.get_trip_options.remote("20200430", "BOS", "DEL")
    car_booker = CarBooker.remote()
    car_options = car_booker.get_trip_options.remote(date, source)

    car_results, flight_results = ray.get([car_options, flight_options])

    print("car results count: " + str(len(car_results)))
    print("flight results count : " + str(len(flight_results)))


