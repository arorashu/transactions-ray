# Trip booking class

import ray

from car_service import CarBooker
from flight_service import FlightBooker


@ray.remote
class TripBooker:
    def __init__(self, trip_db_handle):
        # print("trip booking constructor")
        trip_db = []
        self.trip_db_handle = ray.put(trip_db)

    def get_trip_options(self, date, source, dest):
        print(f"search Trip options for: date {date}, from: {source}, to:{dest}")
        flight_booker = FlightBooker.remote()
        car_booker = CarBooker.remote()
        flight_options = flight_booker.get_trip_options.remote("20200430", "BOS", "DEL")
        car_options = car_booker.get_trip_options.remote(date, source)
        car_results, flight_results = ray.get([car_options, flight_options])
        print("car results count: " + str(len(car_results)))
        print("flight results count : " + str(len(flight_results)))
        return car_results, flight_results


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

    flight_id = flight_results[0]['id']
    print(f"flightId: {flight_id}")
    is_success, trip_details = ray.get(flight_booker.book_trip.remote(flight_id))
    if is_success:
        print(f"Successfully booked: {trip_details}")
    else:
        print("Failed to book flight")

    car_id = car_results[0]['id']
    print(f"car_id: {car_id}")
    is_success, trip_details = ray.get(car_booker.book_trip.remote(car_id))
    if is_success:
        print(f"Successfully booked: {trip_details}")
    else:
        print("Failed to book Car")
