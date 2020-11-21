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

        # A部分信号生成
        re_a = carry * message  # *为星乘，@为点乘
        re_a = Modulate.amplitude * re_a / np.max(np.abs(re_a))

        # B部分信号生成
        re_b = carry.copy()
        re_b = Modulate.amplitude * re_b / np.max(np.abs(re_b))

        return re_a + re_b
