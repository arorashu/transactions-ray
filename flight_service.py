# Trip booking class

import atexit
import json

import ray


@ray.remote
class FlightBooker:
    def __init__(self):
        with open("db/flight_db.json") as f:
            flight_db = json.load(f)
        # list of dict
        self.flight_db_handle = ray.put(flight_db)

        # def cleanup_flight_local():
        #     print("cleanup flight local called")
        #     with open("./flight_db.json", 'w') as f:
        #         json.dump(ray.get(self.flight_db_handle), f, indent=4)
        #
        # atexit.register(cleanup_flight_local)

    def cleanup(self):
        print("cleanup flight class called")
        with open("db/flight_db.json", 'w') as f:
            json.dump(ray.get(self.flight_db_handle), f, indent=4)

    # args: date, source, dest
    # returns: list <flight_options>
    @ray.method(num_return_vals=1)
    def get_trip_options(self, date, source, dest):
        # print(f"search Flight options for: date {date}, from: {source}, to: {dest}")
        flight_db = ray.get(self.flight_db_handle)

        res = []
        for flight_option in flight_db:
            if flight_option['from'] == source and flight_option['to'] == dest and flight_option['date'] == date:
                res.append(flight_option)

        return res

    # currently, can only book 1 seat at a time
    # currently doesn't hold locks
    @ray.method(num_return_vals=2)
    def book_trip(self, flight_id):
        flight_db = ray.get(self.flight_db_handle)
        is_success = False
        trip_details = {}

        for flight_option in flight_db:
            if flight_option['id'] == flight_id and int(flight_option['seats']) > 0:
                is_success = True
                trip_details = flight_option
                flight_option['seats'] = str(int(flight_option['seats']) - 1)
                self.flight_db_handle = ray.put(flight_db)
                break

        updated_flight_db = ray.get(self.flight_db_handle)
        # print("New flight db: " + str(flight_db))
        return is_success, trip_details

    # def cancel_booking(self, flight_id):


def cleanup(flight_booker):
    print("global cleanup called")
    flight_booker.cleanup.remote()
    # del flightBooker


if __name__ == "__main__":
    ray.init()
    flightBooker = FlightBooker.remote()
    atexit.register(cleanup, flightBooker)
    flight_options = ray.get(flightBooker.get_trip_options.remote("20200430", "BOS", "DEL"))
    print(f"flight options: {flight_options}")
    is_success, booking = ray.get(flightBooker.book_trip.remote("1002"))
    is_success, booking = ray.get(flightBooker.book_trip.remote("1002"))
    is_success, booking = ray.get(flightBooker.book_trip.remote("1002"))
    is_success, booking = ray.get(flightBooker.book_trip.remote("1002"))
    is_success, booking = ray.get(flightBooker.book_trip.remote("1002"))
    # del flightBooker
    print(f"booking: {booking}")
