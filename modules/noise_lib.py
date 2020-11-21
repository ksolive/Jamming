import threading, time, os, logging
import wave
import numpy as np

import settings


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
            time.sleep(self.update_cycle)

    def stop(self):
        self.exit_flag = True
        self.join()

    def config_noise_lib(self):
        self.exit_flag = False  # 线程退出标志
        self.update_cycle = 2  # 噪声更新周期

        NoiseLib.f_lower_bound = 50  # 噪声频率下界
        NoiseLib.f_upper_bound = 1000  # 噪声频率上界
        NoiseLib.num_of_base = 10  # 噪声基底个数
        NoiseLib.random_factor = np.random.rand(
            self.num_of_base)  # 初始的噪声基底线性叠加系数

    def load_noise_pairs(self):
        # 获取raw目录下所有音频文件名
        raw_noise_filenames = []
        raw_noise_dir = os.path.join(".\waves", "raw")
        distort_noise_dir = os.path.join(".\waves", "distort")
        for root, dirs, files in os.walk(raw_noise_dir):  # 字符串前+r表示不含转义字符
            for file in files:
                raw_noise_filenames.append(file)

        # 根据文件名读取音频文件
        NoiseLib.raw_noise_data = []
        NoiseLib.distort_noise_data = []
        try:
            for filename in raw_noise_filenames:
                wf1 = wave.open(os.path.join(raw_noise_dir, filename), "rb")
                NoiseLib.raw_noise_data.append(wf1.readframes(
                    wf1.getparams().nframes))  # 一次性读取所有frame

                wf2 = wave.open(os.path.join(distort_noise_dir, filename),
                                "rb")
                NoiseLib.distort_noise_data.append(
                    wf2.readframes(wf2.getparams().nframes))
        except:
            logging.info("Can't find noise file pairs")
            # raise TypeError("Can't find noise file pairs")
        # print(type(NoiseLib.raw_noise_data[0]))
        # print(len(NoiseLib.raw_noise_data[0]))
        # print(NoiseLib.raw_noise_data[0][0:10])

    def update_noise(self):
        NoiseLib.random_factor = np.random.rand(NoiseLib.num_of_base)

    @classmethod
    def read_raw_noise_frames(cls,index,frame_count):
        re = cls.raw_noise_data[index][0:frame_count]
        tmp = bytearray(cls.raw_noise_data[index])
        del tmp[0:frame_count]
        cls.raw_noise_data[index] = bytes(tmp)
        return re

    # 获取浮点数类型的单声道的噪声信号
    @classmethod
    def get_noise_clip(cls, frame_of_noise):
        w_bases = np.linspace(cls.f_lower_bound, cls.f_upper_bound,
                              cls.num_of_base)
        re = np.zeros(shape=(frame_of_noise))
        t = np.linspace(0, frame_of_noise / settings.FS, num=frame_of_noise)
        for i in range(cls.num_of_base):
            re += cls.random_factor[i] * np.sin(
                2 * np.pi * w_bases[i] * t)
        return re / np.max(np.abs(re))  # 归一化
