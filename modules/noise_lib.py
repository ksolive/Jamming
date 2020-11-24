import threading, time, os, logging
import wave
import numpy as np
import matplotlib.pyplot as plt

import settings
import global_var


class NoiseLib(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # 配置噪声库
        self.config_noise_lib()
        # 读取噪声Pairs
        self.load_noise_pairs()
        # 开始运行线程
        self.start()

    def run(self):
        while not self.exit_flag:
            self.update_noise()
            time.sleep(NoiseLib.update_cycle)

    def stop(self):
        self.exit_flag = True
        self.join()

    def config_noise_lib(self):
        self.exit_flag = False  # 线程退出标志

        NoiseLib.update_cycle = 4  # 噪声更新周期
        NoiseLib.f_lower_bound = 20  # 噪声频率下界
        NoiseLib.f_upper_bound = 20  # 噪声频率上界
        NoiseLib.num_of_base = 1  # 噪声基底个数

        NoiseLib.random_noise = np.zeros(
            shape=(settings.OUT_FS * NoiseLib.update_cycle))  # 初始的噪声
        NoiseLib.read_index = 0  # 保存noise读取历史

    def update_noise(self):
        global_var.mutex_noise.acquire()  # 互斥更新noise

        frame_of_noise = settings.OUT_FS * NoiseLib.update_cycle
        random_factor = np.random.rand(NoiseLib.num_of_base)
        w_bases = np.linspace(NoiseLib.f_lower_bound, NoiseLib.f_upper_bound,
                              NoiseLib.num_of_base)
        t = np.linspace(0, NoiseLib.update_cycle, num=frame_of_noise)
        NoiseLib.random_noise = np.zeros(shape=(frame_of_noise))
        for i in range(NoiseLib.num_of_base):
            NoiseLib.random_noise += random_factor[i] * np.sin(
                2 * np.pi * w_bases[i] * t)
        NoiseLib.random_noise = NoiseLib.random_noise / np.max(
            np.abs(NoiseLib.random_noise))
        NoiseLib.read_index = 0

        global_var.mutex_noise.release()

    def load_noise_pairs(self):
        # 获取raw目录下所有音频文件名
        raw_noise_filenames = []
        raw_noise_dir = os.path.join(".\waves", "raw")
        for root, dirs, files in os.walk(raw_noise_dir):  # 字符串前+r表示不含转义字符
            for file in files:
                raw_noise_filenames.append(file)

        # 根据文件名读取音频文件
        NoiseLib.raw_noise_data = []
        try:
            for filename in raw_noise_filenames:
                wf = wave.open(os.path.join(raw_noise_dir, filename), "rb")
                framerate = wf.getparams().framerate
                read_index = 0
                sampwidth = wf.getparams().sampwidth
                nframes = wf.getparams().nframes
                data = wf.readframes(nframes)  # 一次性读取所有frame
                NoiseLib.raw_noise_data.append(
                    [read_index, sampwidth, nframes, data])
        except:
            raise TypeError("Can't find noise file pairs")

        # print(r"\x"+r" \x".join(format(x,'02x') for x in NoiseLib.raw_noise_data[0][7200:7220]))  # 原始十六进制表示

    # 获取bytes类型的声音信号
    @classmethod
    def get_wave_bytes_buffer(cls, index, frame_count=-1):
        if frame_count == -1:
            return cls.raw_noise_data[index][-1]

        read_index, sampwidth, nframes, data = cls.raw_noise_data[index]
        start_index = read_index
        end_index = read_index + frame_count * sampwidth
        if end_index >= nframes:
            re = data[start_index:-1] + data[0:end_index % nframes]
        else:
            re = data[start_index:end_index]
        cls.raw_noise_data[index][0] = end_index % nframes
        return re

    # 获取float类型的噪声信号
    @classmethod
    def get_noise_clip(cls, frame_count=-1):
        global_var.mutex_noise.acquire()  # 互斥读取noise

        if frame_count == -1:
            cls.read_index = 0
            global_var.mutex_noise.release()
            return cls.random_noise[0:-1]

        frame_of_noise = settings.OUT_FS * cls.update_cycle
        start_index = cls.read_index
        end_index = start_index + frame_count
        if end_index >= frame_of_noise:
            re = cls.random_noise[start_index:-1] + cls.random_noise[
                0:end_index % frame_of_noise]
        else:
            re = cls.random_noise[start_index:end_index]
        cls.read_index = end_index % frame_of_noise

        global_var.mutex_noise.release()

        return re