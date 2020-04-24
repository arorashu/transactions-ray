# Trip booking class

import json

import ray


@ray.remote
class UserService:

    def __init__(self):
        # list of dict
        with open("db/user_db.json") as f:
            user_db = json.load(f)
        self.user_db_handle = ray.put(user_db)

    def cleanup(self):
        print("user cleanup called")
        user_db = ray.get(self.user_db_handle)
        print(f"user db write: {user_db}")
        with open('db/user_db.json', 'w') as f:
            json.dump(ray.get(self.user_db_handle), f, indent=4)

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
        error_msg = ""

        for user in user_db:
            if user['id'] == user_id:
                user['bookings'][trip_id] = True
                self.user_db_handle = ray.put(user_db)
                is_success = True
                break

        if is_success is False:
            error_msg = f"user with id: {user_id} not found"

        return is_success, error_msg

    def cancel_booking(self, user_id, trip_id):
        user_db = ray.get(self.user_db_handle)
        is_success = False
        error_msg = ""

        for user in user_db:
            if user['id'] == user_id:
                # TODO: check if trip id exists for user
                user['bookings'][trip_id] = False
                self.user_db_handle = ray.put(user_db)
                is_success = True
                break

        if is_success is False:
            error_msg = f"user with id: {user_id} not found"

        return is_success, error_msg


if __name__ == "__main__":
    ray.init()
    userService = UserService.remote()
    user_id = "3001"
    user_details = ray.get(userService.get_user_details.remote(user_id))
    print(f"user details: {user_details}")
