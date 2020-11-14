import pyaudio
import time

class IOManager():
    def __init__(self):
        self.run()
        
    def run(self):
        self.pa = pyaudio.PyAudio()
        # self.stream = self.pa.open(format=pyaudio.paInt8,
        #         channels=1,
        #         rate=16000,
        #         input=True,
        #         output=False,
        #         frames_per_buffer=2048,
        #         stream_callback=IOManager.read_audio)
        self.stream = self.pa.open(format=pyaudio.paInt8,
                channels=1,
                rate=16000,
                input=False,
                output=True,
                frames_per_buffer=2048,
                stream_callback=IOManager.write_audio)
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
    
    @staticmethod
    def read_audio(in_data, frame_count, time_info, status):
        print("Read")
        return (None, pyaudio.paContinue)

    @staticmethod
    def write_audio(in_data, frame_count, time_info, status):
        print("Write")
        return (None, pyaudio.paContinue)

    
