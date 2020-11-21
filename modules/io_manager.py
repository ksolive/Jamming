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
                                       channels=settings.INPUT_CHANNEL,
                                       rate=settings.FS,
                                       input=True,
                                       output=False,
                                       frames_per_buffer=2048,
                                       stream_callback=IOManager.read_audio)
        except:
            logging.warning("No input device detected!")
        try:
            self.stream = self.pa.open(format=settings.OUTPUT_FORMAT,
                                       channels=settings.OUTPUT_CHANNEL,
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

    # 将bytes类型的字节流转换为归一化的float ndarray
    @staticmethod
    def decode_single_channel(bytes_buffer):
        # 检查
        if not isinstance(bytes_buffer, bytes):
            logging.error("Input buffer must be bytes!")
            return bytes_buffer

        # 根据输入类型确定split步长
        if settings.INPUT_FORMAT == pyaudio.paInt16:
            split_step = 2
        elif settings.INPUT_FORMAT == pyaudio.paInt24:
            split_step = 3
        elif settings.INPUT_FORMAT == pyaudio.paInt24:
            split_step = 4

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
        channel = channel / np.max(np.abs(channel))
        re = channel

        return re

    @staticmethod
    def decode_double_channel(bytes_buffer):
        # 检查
        if not isinstance(bytes_buffer, bytes):
            logging.error("Input buffer must be bytes!")
            return bytes_buffer

        # 根据输入类型确定split步长
        if settings.INPUT_FORMAT == pyaudio.paInt16:
            split_step = 4
        elif settings.INPUT_FORMAT == pyaudio.paInt24:
            split_step = 6
        elif settings.INPUT_FORMAT == pyaudio.paInt24:
            split_step = 8

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
        left_channel = left_channel / np.max(np.abs(left_channel))
        re_left = left_channel

        right_channel = np.array([
            int.from_bytes(xi, byteorder='little', signed=True)
            for xi in right_channel
        ]).astype(np.float64)
        right_channel = right_channel / np.max(np.abs(right_channel))
        re_right = right_channel

        return re_left, re_right

    # 将float类型的ndarray根据扬声器采样深度编码为可以发送的bytes，单声道版本
    @staticmethod
    def encode_single_channel(audio_clip):
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
    def encode_double_channel(audio_clip_left, audio_clip_right):
        # 检查
        if not isinstance(audio_clip_left, np.ndarray) or not isinstance(
                audio_clip_right, np.ndarray):
            logging.error("Input audio clip must be numpy array!")
            return audio_clip_left

        if audio_clip_left.shape != audio_clip_right.shape:
            logging.error("Shape of input audio clip must be the same!")
            return audio_clip_left

        if audio_clip_left.dtype not in (np.float64, np.float32, np.float16):
            logging.error("Input audio clip must be float numpy!")
            return audio_clip_left
        elif audio_clip_right.dtype not in (np.float64, np.float32,
                                            np.float16):
            logging.error("Input audio clip must be float numpy!")
            return audio_clip_left

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
        # 数据类型转换：bytes->float ndarray，并且写入全局队列
        if settings.INPUT_CHANNEL == 1:
            audio_clip = IOManager.decode_single_channel(in_data)
            global_var.write_data.put(audio_clip)

        elif settings.INPUT_CHANNEL == 2:
            audio_clip_left, audio_clip_right = IOManager.decode_double_channel(
                in_data)
            global_var.write_data.put(audio_clip_left)  # ???
        return (None, pyaudio.paContinue)

    @staticmethod
    def write_audio(in_data, frame_count, time_info, status):
        # 获取噪声
        noise_clip = NoiseLib.get_noise_clip(frame_count)
        # 数据类型转换：float ndarray->bytes
        if settings.OUTPUT_CHANNEL == 1:
            noise_clip = Modulate.am_modulate_single_channel(noise_clip)
            out_data = IOManager.encode_single_channel(noise_clip)
        elif settings.OUTPUT_CHANNEL == 2:
            noise_clip_left, noise_clip_right = Modulate.am_modulate_double_channel(
                noise_clip)
            out_data = IOManager.encode_double_channel(noise_clip_left,
                                                       noise_clip_right)

        return (out_data, pyaudio.paContinue)
