# app service that runs the trip booking app

import atexit
import ray

from trip_service import TripBooker
from user_service import UserService



def cleanup(actor_list):
    print("global cleanup called")
    for actor in actor_list:
        actor.cleanup.remote()
        # del actor


if __name__ == "__main__":
    print("started app service")
    ray.init()
    userService = UserService.remote()
    tripService = TripBooker.remote()
    atexit.register(cleanup, [userService, tripService])

    date = "20200430"
    source = "BOS"
    destination = "DEL"
    user_id = "3000"
    car_results, flight_results = ray.get(tripService.get_trip_options.remote(date, source, destination))
    print(f"car results: {car_results}")

    flight_id = flight_results[0]['id']
    print(f"flightId: {flight_id}")
    car_id = car_results[0]['id']
    print(f"car_id: {car_id}")

    is_success, trip_id = ray.get(tripService.make_booking.remote(user_id, flight_id, car_id))
    is_success, error_msg = ray.get(userService.make_booking.remote(user_id, trip_id))

    print(f"trip id: {trip_id}")

