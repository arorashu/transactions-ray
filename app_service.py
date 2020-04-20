# app service that runs the trip booking app

import ray

from trip_service import TripBooker
from user_service import UserService


if __name__ == "__main__":
    print("started app service")
    ray.init()
    trip_db_handle = ray.put([])
    userService = UserService.remote()
    tripService = TripBooker.remote(trip_db_handle)
    date = "20200430"
    source = "BOS"
    destination = "DEL"
    car_results, flight_results = ray.get(tripService.get_trip_options.remote(date, source, destination))
    print(f"car results: {car_results}")

    # flight_id = flight_results[0]['id']
    # print(f"flightId: {flight_id}")
    # is_success, trip_details = ray.get(flight_booker.book_trip.remote(flight_id))
    # if is_success:
    #     print(f"Successfully booked: {trip_details}")
    # else:
    #     print("Failed to book flight")
    #
    # car_id = car_results[0]['id']
    # print(f"car_id: {car_id}")
    # is_success, trip_details = ray.get(car_booker.book_trip.remote(car_id))
    # if is_success:
    #     print(f"Successfully booked: {trip_details}")
    # else:
    #     print("Failed to book Car")
