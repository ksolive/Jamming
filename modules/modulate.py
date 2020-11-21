import numpy as np
import logging

import settings


class Modulate():
    f_c = 40000  # 载波频率
    amplitude = 0.9  # 归一化幅度

    def __init__(self):
        pass

    # 单声道AM调制
    @staticmethod
    def am_modulate_single_channel(message):
        # 检查
        if not isinstance(message, np.ndarray):
            logging.error("Input message must be numpy array!")
            return message

        if message.ndim != 1:
            logging.error("Input message must be 1D!")
            return message

        # 生成载波信号
        t = np.linspace(0, message.size / settings.FS, num=message.size)
        carry = np.sin(2 * np.pi * Modulate.f_c * t)

        # 左声道部分信号生成
        re_left = carry * message  # *为星乘，@为点乘
        re_left = Modulate.amplitude * re_left / np.max(np.abs(re_left))

        # 右声道部分信号生成
        re_right = carry.copy()
        re_right = Modulate.amplitude * re_right / np.max(np.abs(re_right))

        return re_left + re_right

    # 双声道AM调制
    @staticmethod
    def am_modulate_double_channel(message):
        # 检查
        if not isinstance(message, np.ndarray):
            logging.error("Input message must be numpy array!")
            return message

        if message.ndim != 1:
            logging.error("Input message must be 1D!")
            return message

        # 生成载波信号
        t = np.linspace(0, message.size / settings.FS, num=message.size)
        carry = np.sin(2 * np.pi * Modulate.f_c * t)

        # 左声道部分信号生成
        re_left = carry * message  # *为星乘，@为点乘
        re_left = Modulate.amplitude * re_left / np.max(np.abs(re_left))

        # 右声道部分信号生成
        re_right = carry.copy()
        re_right = Modulate.amplitude * re_right / np.max(np.abs(re_right))

        return (re_left, re_right)
