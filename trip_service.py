# Trip booking class

import ray

from car_service import CarBooker
from flight_service import FlightBooker


@ray.remote
class TripBooker:
    def __init__(self, trip_db_handle):
        self.trip_db_handle = trip_db_handle
        self.flight_booker = FlightBooker.remote()
        self.car_booker = CarBooker.remote()
        # Question: which method to use to instantiate services?
        # have a list of services and then round robin?
        # how to load balance?
        # different implementation in get trip and make booking

    # def __init__(self):
    #     trip_db = []
    #     self.trip_db_handle = ray.put(trip_db)


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

    def make_booking(self, flight_id, car_id):
        flight_booker, car_booker = self.flight_booker, self.car_booker
        is_success, trip_details = ray.get(flight_booker.book_trip.remote(flight_id))
        if is_success:
            print(f"Successfully booked: {trip_details}")
        else:
            print("Failed to book flight")
        is_success, trip_details = ray.get(car_booker.book_trip.remote(car_id))
        if is_success:
            print(f"Successfully booked: {trip_details}")
        else:
            print("Failed to book Car")


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
