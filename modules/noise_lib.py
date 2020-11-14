import threading

class NoiseLib1(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        print("Thread1")

    @classmethod
    def get_noise_clip(cls):
        return "***"

class NoiseLib2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        print(NoiseLib1.get_noise_clip())
