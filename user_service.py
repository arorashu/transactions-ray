# Trip booking class

import ray
import time
import json


@ray.remote
class UserService:

    def __init__(self):
        # list of dict
        with open("./user_db.json") as f:
            user_db = json.load(f)
        self.user_db_handle = ray.put(user_db)

    def get_user_details(self, user_id):
        user_db = ray.get(self.user_db_handle)
        res = {}
        for user in user_db:
            if user['id'] == user_id:
                res = user
        return res

    # currently, can only book 1 car at a time
    # currently doesn't hold locks
    def make_booking(self, user_id, trip_id):
        user_db = ray.get(self.user_db_handle)
        is_success = False
        trip_details = {}

        for user in user_db:
            if user['id'] == user_id:
                user['bookings'].append(trip_id)
                self.user_db_handle = ray.put(user_db)
                is_success = True
                break

        return is_success, trip_details


if __name__ == "__main__":
    ray.init()
    userService = UserService.remote()
    user_id = "3001"
    user_details = ray.get(userService.get_user_details.remote(user_id))
    print(f"user details: {user_details}")
