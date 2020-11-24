import numpy as np
import logging

import settings


class Modulate():
    f_c = 40000  # 载波频率
    amplitude = 1  # 归一化幅度

    def __init__(self):
        pass

    # AM调制
    @classmethod
    def am_modulate(cls, audio_clip, channel=1):
        # 检查
        if not isinstance(audio_clip, np.ndarray):
            raise TypeError("Input audio clip must be numpy array!")

        if audio_clip.dtype not in (np.float64, np.float32, np.float16):
            raise TypeError("Input audio clip must be float numpy!")

        if audio_clip.ndim != 1:
            raise ValueError("Input message must be 1D!")

        if channel not in (1, 2):
            raise ValueError("Input channel must be 1 or 2!")

        # 生成载波信号
        t = np.linspace(0, audio_clip.size / settings.OUT_FS, num=audio_clip.size)
        carry = np.sin(2 * np.pi * cls.f_c * t)

        # 左声道部分信号生成
        re_left = carry * audio_clip  # *为星乘，@为点乘

        # 右声道部分信号生成
        re_right = carry.copy()

        if channel == 1:
            re = re_left + re_right
            return cls.amplitude * re / np.max(np.abs(re))
        else:
            return (cls.amplitude * re_left, cls.amplitude * re_right)
