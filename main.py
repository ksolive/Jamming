from modules.noise_lib import NoiseLib1, NoiseLib2
from modules.io_manager import IOManager
import pyaudio
import time

# def callback(in_data, frame_count, time_info, status):
#     return (data, pyaudio.paContinue)

def run():
    # t1 = NoiseLib1()
    # t2 = NoiseLib2()

    # t1.join()
    # t2.join()
    t1 = IOManager()
    

    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()