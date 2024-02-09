import random
import time

class DataSpoofing:
    def __init__(self, length):
        self.length = length

    def generate_data(self):
        # Generate pseudo-random data of pre-determined length
        data = [random.randint(0, 100) for _ in range(self.length)]
        return data

    def spoof_continuous(self):
        # Run continuously and generate data streams
        while True:
            data_point = self.generate_data()
            time.sleep(1)
            return data_point



if __name__ == "__main__":
    # Example usage
    ds = DataSpoofing(5)
    while True:
        try:
            print(ds.spoof_continuous())
        except KeyboardInterrupt:
            break
    