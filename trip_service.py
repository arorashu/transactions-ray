# Trip booking class

import json

import ray

from car_service import CarBooker
from flight_service import FlightBooker


@ray.remote
class TripBooker:
    def __init__(self):

        with open("./trip_db.json") as f:
            trip_db = json.load(f)

        self.trip_db_handle = ray.put(trip_db)
        print(f"loaded trip db: {trip_db}")
        self.new_trip_id = int(max(trip_db.keys())) + 1
        self.flight_booker = FlightBooker.remote()
        self.car_booker = CarBooker.remote()
        # Question: which method to use to instantiate services?
        # have a list of services and then round robin?
        # how to load balance?
        # different implementation in get trip and make booking

    def cleanup(self):
        print("cleanup trip called")
        self.flight_booker.cleanup.remote()
        self.car_booker.cleanup.remote()
        # print(f"writing trip db: {trip_db}")
        with open("./trip_db.json", 'w') as f:
            json.dump(ray.get(self.trip_db_handle), f, indent=4)

    def get_trip_options(self, date, source, dest):
        print(f"search Trip options for: date {date}, from: {source}, to:{dest}")
        flight_booker = self.flight_booker
        car_booker = self.car_booker
        flight_options = flight_booker.get_trip_options.remote("20200430", "BOS", "DEL")
        car_options = car_booker.get_trip_options.remote(date, source)
        car_results, flight_results = ray.get([car_options, flight_options])
        print("car results count: " + str(len(car_results)))
        print("flight results count : " + str(len(flight_results)))
        return car_results, flight_results

    def make_booking(self, user_id, flight_id, car_id):
        flight_booker, car_booker = self.flight_booker, self.car_booker
        trip_details = {
            'id': self.new_trip_id,
            'user_id': user_id
        }

        is_flight_success, flight_details = ray.get(flight_booker.book_trip.remote(flight_id))
        if is_flight_success:
            print(f"Successfully booked: {flight_details}")
            trip_details['flight_booking_id'] = flight_id
        else:
            print("Failed to book flight")
        is_car_success, car_details = ray.get(car_booker.book_trip.remote(car_id))
        if is_car_success:
            print(f"Successfully booked: {car_details}")
            trip_details['car_booking_id'] = car_id
        else:
            print("Failed to book Car")

        trip_id = -1
        is_success = False
        if is_car_success and is_flight_success:
            is_success = True
            trip_id = self.new_trip_id
            print(f"trip db handle: {self.trip_db_handle}")
            trip_db = ray.get(self.trip_db_handle)
            trip_db[trip_id] = trip_details
            self.trip_db_handle = ray.put(trip_db)
            self.new_trip_id += 1

        return is_success, trip_id


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
