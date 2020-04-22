import atexit
import json

import ray


@ray.remote
class B:
    def __init__(self):
        print("B constructor")

        # def cleanup_local():
        #     print("B release resources")
        #
        # atexit.register(cleanup_local)
        atexit.register(self.cleanup)

    def cleanup(self):
        print("B release resources")
        with open("./examples/cleanup2-out.json", "w") as file:
            json.dump({"cleanup2": "true"}, file)

    # # def __del__(self):
    #     print("B delete release resources")


ray.init()
b = B.remote()
# del b
print("ray complete")
