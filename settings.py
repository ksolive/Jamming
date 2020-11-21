import pyaudio

FS = 48000  # 采样率

INPUT_CHANNEL = 2  # 麦克风输入通道数
INPUT_FORMAT = pyaudio.paInt24  # 麦克风采样深度

OUTPUT_CHANNEL = 2  # 扬声器输出通道数
OUTPUT_FORMAT = pyaudio.paInt24  # 扬声器采样深度

