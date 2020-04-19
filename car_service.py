# Trip booking class

import ray
import time
import json


@ray.remote
class CarBooker:

    def __init__(self):
        print("car booking constructor")

        # list of dict
        with open("./car_db.json") as f:
            self.car_db = json.load(f)

    def get_trip_options(self, date, airport):
        print(f"search Car options to airport: date {date}, airport: {airport}")
        car_db = self.car_db

        res = []
        for car in car_db:
            if car['airport'] == airport and car['date'] == date:
                res.append(car)

        return res


if __name__ == "__main__":
    carBooker = CarBooker()
    carBooker.get_trip_options("20200416", "Boston", "Delhi")

