import pyaudio
import logging, sys, time, os, datetime
import matplotlib.pyplot as plt
import numpy as np

from modules.modulate import Modulate
from modules.noise_lib import NoiseLib
from modules.io_manager import IOManager
from modules.ars import ASRManager

import global_var
import settings

def run():
    # 启动程序
    config_logging()
    logging.info("Start jamming programmer")
    _ = Modulate()
    noiselib_thread = NoiseLib()
    io_threads = IOManager()
    # asr默认初始化两个进程进行
    asr_Manager = ASRManager()
    asr_Manager.create_asr_thread()
    asr_Manager.create_asr_thread()

    try:
        plt.ion()
        plt.figure(1)
        while True:
            show_data()
    except:
        # 停止程序
        logging.info("Stop jamming programmer")
        noiselib_thread.stop()
        io_threads.stop()
        asr_Manager.kill_all()

def config_logging():
    if not os.path.exists("logs"):
        os.mkdir("logs")
    
    log_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M") + ".log"
    log_filepath = os.path.join(os.path.join(os.getcwd(), "logs"),
                                log_filename)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(stream=sys.stdout)
    fh = logging.FileHandler(filename=log_filepath, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)  # 日志输出到终端
    logger.addHandler(fh)  # 日志输出到文件
    logging.getLogger('matplotlib.font_manager').disabled = True  # 禁用字体管理记录器

    logging.info("Current log file {}".format(log_filepath))


def show_data():
        plt.xlim((global_var.run_time - 4, global_var.run_time + 4))

        while not global_var.write_data.empty():
            start_time = global_var.run_time
            end_time = global_var.run_time + settings.FRAMES_PER_BUFFER / settings.IN_FS
            global_var.run_time = end_time
            t = np.linspace(start_time, end_time, settings.FRAMES_PER_BUFFER)
            y = global_var.write_data.get()
        
            plt.plot(t, y,"r")
        plt.pause(0.1)


if __name__ == "__main__":
    run()