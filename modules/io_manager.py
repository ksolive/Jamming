import pyaudio
import time, logging
import numpy as np
import pyaudio
import matplotlib.pyplot as plt

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
            self.stream = self.pa.open(
                format=settings.INPUT_FORMAT,
                channels=settings.INPUT_CHANNEL,
                rate=settings.IN_FS,
                input=True,
                output=False,
                frames_per_buffer=settings.FRAMES_PER_BUFFER,
                stream_callback=IOManager.read_audio)
        except:
            logging.warning("No input device detected!")
        try:
            self.stream = self.pa.open(
                format=settings.OUTPUT_FORMAT,
                channels=settings.OUTPUT_CHANNEL,
                rate=settings.OUT_FS,
                input=False,
                output=True,
                frames_per_buffer=settings.FRAMES_PER_BUFFER,
                stream_callback=IOManager.write_audio)
        except:
            logging.warning("No output device detected!")

        self.stream.start_stream()

    def stop(self):
        # y = np.array([])
        # for i in range(10):
        #     y = np.append(y, NoiseLib.get_noise_clip(10000),axis=0)
        # plt.plot(y)
        # plt.show()
        # noise_clip = IOManager.decode_single_channel(
        #     NoiseLib.get_wave_bytes_buffer(0))

        # noise_clip = Modulate.am_modulate_single_channel(noise_clip)
        # out_data = IOManager.encode_single_channel(noise_clip)
        # import wave
        # wf1 = wave.open(r".\waves\modulated\yes_no_left.wav", "wb")
        # # wf2 = wave.open(r".\waves\modulated\yes_no_right.wav","wb")

        # wf1.setnchannels(1)
        # wf1.setsampwidth(3)
        # wf1.setframerate(8000)
        # wf1.writeframes(out_data)

        # 关闭时可能超时，所以使用try
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
        except:
            pass

    # 将bytes类型的字节流转换为归一化的float ndarray
    @staticmethod
    def decode_bytes_to_audio(bytes_buffer):
        # 检查
        if not isinstance(bytes_buffer, bytes):
            logging.error("Input buffer must be bytes!")
            return bytes_buffer

        if settings.INPUT_CHANNEL not in (1, 2):
            raise ValueError("Input channel must be 1 or 2!")

        # 根据输入类型确定split步长
        if settings.INPUT_FORMAT == pyaudio.paInt16:
            split_step = 2 * settings.INPUT_CHANNEL
            max_value = 2**15
        elif settings.INPUT_FORMAT == pyaudio.paInt24:
            split_step = 3 * settings.INPUT_CHANNEL
            max_value = 2**23
        elif settings.INPUT_FORMAT == pyaudio.paInt32:
            split_step = 4 * settings.INPUT_CHANNEL
            max_value = 2**31

        if settings.INPUT_CHANNEL == 1:
            # 获取声道信息
            channel = []
            length = len(bytes_buffer)
            for i in range(0, length, split_step):
                channel.append(bytes_buffer[i:i + split_step])

            # 转化为ndarray并且归一化
            channel = np.array([
                int.from_bytes(xi, byteorder='little', signed=True)
                for xi in channel
            ]).astype(np.float64)
            channel = channel / max_value
            re = channel

            return re
        else:
            # 左右声道拆分
            left_channel = []
            right_channel = []
            length = len(bytes_buffer)
            for i in range(0, length, split_step):
                left_channel.append(bytes_buffer[i:i + int(split_step / 2)])
                right_channel.append(bytes_buffer[i + int(split_step / 2):i +
                                                  split_step])

            # 转化为ndarray并且归一化
            left_channel = np.array([
                int.from_bytes(xi, byteorder='little', signed=True)
                for xi in left_channel
            ]).astype(np.float64)
            left_channel = left_channel / max_value
            re_left = left_channel

            right_channel = np.array([
                int.from_bytes(xi, byteorder='little', signed=True)
                for xi in right_channel
            ]).astype(np.float64)
            right_channel = right_channel / np.max(np.abs(right_channel))
            re_right = right_channel

            return (re_left, re_right)

    # 将float类型的ndarray根据扬声器采样深度编码为可以发送的bytes
    @staticmethod
    def encode_audio_to_bytes(audio_clip):
        if settings.OUTPUT_CHANNEL not in (1, 2):
            raise ValueError("Input channel must be 1 or 2!")

        if settings.OUTPUT_CHANNEL == 1:
            # 单声道检查
            if not isinstance(audio_clip, np.ndarray):
                raise TypeError("Input audio clip must be numpy array!")

            if audio_clip.dtype not in (np.float64, np.float32, np.float16):
                raise TypeError("Input audio clip must be float numpy!")
        else:
            # 双声道检查
            audio_clip_left = audio_clip[0]
            audio_clip_right = audio_clip[1]
            if not isinstance(audio_clip_left, np.ndarray) or not isinstance(
                    audio_clip_right, np.ndarray):
                raise TypeError("Input audio clip must be numpy array!")

            if audio_clip_left.dtype not in (
                    np.float64, np.float32,
                    np.float16) or audio_clip_right.dtype not in (np.float64,
                                                                  np.float32,
                                                                  np.float16):
                raise TypeError("Input audio clip must be float numpy!")

            if audio_clip_left.shape != audio_clip_right.shape:
                raise ValueError("Shape of input audio clip must be the same!")

            # 左右声道填充
            audio_clip = []
            for i in range(audio_clip_left.size):
                audio_clip.append(audio_clip_left[i])
                audio_clip.append(audio_clip_right[i])
            audio_clip = np.array(audio_clip)

        # 根据扬声器采样深度进行转化
        if settings.OUTPUT_FORMAT == pyaudio.paInt16:
            re = (audio_clip * 2**15).clip(-2**15, 2**15 - 1).astype(
                np.int16).tobytes()
        elif settings.OUTPUT_FORMAT == pyaudio.paInt24:
            re = b""
            for i in range(audio_clip.size):
                tmp = int((audio_clip[i] * 2**23).clip(-2**23, 2**23 - 1))
                re += tmp.to_bytes(3, byteorder='little', signed=True)
        elif settings.OUTPUT_FORMAT == pyaudio.paInt32:
            re = (audio_clip * 2**31).clip(-2**31, 2**31 - 1).astype(
                np.int32).tobytes()
        else:
            raise TypeError("Input audio clip type error!")

        return re

    @staticmethod
    def read_audio(in_data, frame_count, time_info, status):
        # 数据类型转换：bytes->float ndarray，并且写入全局队列
        audio_clip = IOManager.decode_bytes_to_audio(in_data)
        global_var.write_data.put(audio_clip)

        return (None, pyaudio.paContinue)

    @staticmethod
    def write_audio(in_data, frame_count, time_info, status):
        # 获取噪声
        noise_clip = NoiseLib.get_noise_clip(frame_count)

        # noise_clip = Modulate.am_modulate(noise_clip)
        noise_clip = Modulate.pm_modulate(noise_clip)
        out_data = IOManager.encode_audio_to_bytes(noise_clip)

        return (out_data, pyaudio.paContinue)