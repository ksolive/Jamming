import pyaudio
import time, logging
import numpy as np
import pyaudio

import global_var
import settings
from modules.modulate import Modulate
from modules.noise_lib import NoiseLib


class IOManager():
    def __init__(self):
        self.run()

    def run(self):
        self.pa = pyaudio.PyAudio()
        try:
            self.stream = self.pa.open(format=settings.INPUT_FORMAT,
                                       channels=settings.INPUT_CHAANEL,
                                       rate=settings.FS,
                                       input=True,
                                       output=False,
                                       frames_per_buffer=2048,
                                       stream_callback=IOManager.read_audio)
        except:
            logging.warning("No input device detected!")
        try:
            self.stream = self.pa.open(format=settings.OUTPUT_FORMAT,
                                       channels=settings.OUTPUT_CHAANEL,
                                       rate=settings.FS,
                                       input=False,
                                       output=True,
                                       frames_per_buffer=2048,
                                       stream_callback=IOManager.write_audio)
        except:
            logging.warning("No output device detected!")

        self.stream.start_stream()

    def stop(self):
        # 关闭时可能超时，所以使用try
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
        except:
            pass

    # 将float类型的ndarray根据扬声器采样深度编码为可以发送的bytes
    @staticmethod
    def encode_float_ndarray(audio_clip):
        # 检查
        if not isinstance(audio_clip, np.ndarray):
            logging.error("Input audio clip must be numpy array!")
            return audio_clip

        if audio_clip.dtype not in (np.float64, np.float32, np.float16):
            logging.error("Input audio clip must be float numpy!")
            return audio_clip

        # 根据扬声器采样深度进行转化
        if settings.OUTPUT_FORMAT == pyaudio.paInt16:
            re = (audio_clip * 2**15).clip(-2**15, 2**15 - 1).astype(
                np.int16).tobytes()
        elif settings.OUTPUT_FORMAT == pyaudio.paInt24:
            # 转化为小端模式的字节序列
            tmp = (audio_clip * 2**23).clip(-2**23, 2**23 - 1).astype(
                np.int32).tobytes()
            # 将4 bytes转3 bytes
            tmp = bytearray(tmp)
            length = len(tmp)
            for i in range(length)[::-1]:
                if i + 1 % 4 == 0:  # 小端模式删除方式
                    del tmp[i]
            re = bytes(tmp)
        elif settings.OUTPUT_FORMAT == pyaudio.paInt32:
            re = (audio_clip * 2**31).clip(-2**31, 2**31 - 1).astype(
                np.int32).tobytes()
        else:
            logging.error("Input audio clip type error!")
            return audio_clip

        return re

    @staticmethod
    def read_audio(in_data, frame_count, time_info, status):
        global_var.write_data.put(in_data)
        return (None, pyaudio.paContinue)

    @staticmethod
    def write_audio(in_data, frame_count, time_info, status):
        noise_clip = NoiseLib.get_noise_clip_single_channel(frame_count)
        out_data = IOManager.encode_float_ndarray(noise_clip)
        return (out_data, pyaudio.paContinue)
