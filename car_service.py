# Trip booking class

import ray
import time
import json


@ray.remote
class CarBooker:

    def __init__(self):
        # list of dict
        with open("./car_db.json") as f:
            car_db = json.load(f)
        self.car_db_handle = ray.put(car_db)

    def get_trip_options(self, date, airport):
        # print(f"search Car options to airport: date {date}, airport: {airport}")
        car_db = ray.get(self.car_db_handle)
        res = []
        for car in car_db:
            if car['airport'] == airport and car['date'] == date:
                res.append(car)
        return res

    # currently, can only book 1 car at a time
    # currently doesn't hold locks
    def book_trip(self, car_id):
        car_db = ray.get(self.car_db_handle)
        is_success = False
        trip_details = {}

        for car_option in car_db:
            if car_option['id'] == car_id:
                is_success = True
                trip_details = car_option
                ## TODO: do something with car DB
                self.car_db_handle = ray.put(car_db)
                break

        # updated_car_db = ray.get(self.car_db_handle)
        # print("New flight db: " + str(updated_car_db))
        return is_success, trip_details


if __name__ == "__main__":
    carBooker = CarBooker()
    carBooker.get_trip_options("20200430", "BOS", "DEL")

