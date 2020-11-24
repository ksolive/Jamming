import pyaudio

FRAMES_PER_BUFFER = 1024*4

IN_FS = 48000  # 麦克风采样率
INPUT_CHANNEL = 1  # 麦克风输入通道数
INPUT_FORMAT = pyaudio.paInt16  # 麦克风采样深度

OUT_FS = 96000  # 扬声器采样率
OUTPUT_CHANNEL = 2  # 扬声器输出通道数
OUTPUT_FORMAT = pyaudio.paInt24  # 扬声器采样深度