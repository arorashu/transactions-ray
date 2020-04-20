# Trip booking class

import json

import ray


@ray.remote
class FlightBooker:
    def __init__(self):
        with open("./flight_db.json") as f:
            flight_db = json.load(f)
        # list of dict
        self.flight_db_handle = ray.put(flight_db)

    # @ray.remote spans a new process (new pid), anything that you print here
    # does not show on the console, unless you do a ray.get() on the calling process
    #

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
    def book_trip(self, flight_id):
        flight_db = ray.get(self.flight_db_handle)
        is_success = False
        trip_details = {}

        for flight_option in flight_db:
            if flight_option['id'] == flight_id:
                is_success = True
                trip_details = flight_option
                flight_option['seats'] = str(int(flight_option['seats']) - 1)
                self.flight_db_handle = ray.put(flight_db)
                break

        updated_flight_db = ray.get(self.flight_db_handle)
        # print("New flight db: " + str(flight_db))
        return is_success, trip_details


if __name__ == "__main__":
    flightBooker = FlightBooker()
    flightBooker.get_trip_options("20200430", "BOS", "DEL")
