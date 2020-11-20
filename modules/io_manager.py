import pyaudio
import time
import globals

class IOManager():
    def __init__(self):
        self.run()
        
    def run(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16,
                channels=2,
                rate=16000,
                input=True,
                output=False,
                frames_per_buffer=2048,
                stream_callback=IOManager.read_audio)
        self.stream = self.pa.open(format=pyaudio.paInt16,
                channels=2,
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
        global_var.write_data.put(in_data)
        return (None, pyaudio.paContinue)

    @staticmethod
    def write_audio(in_data, frame_count, time_info, status):
        write_data = global_var.write_data.get()
        return (write_data, pyaudio.paContinue)

    
