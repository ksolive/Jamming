import pyaudio
import logging, sys, time, os, datetime

from modules.noise_lib import NoiseLib
from modules.io_manager import IOManager

def run():
    # 启动程序
    config_logging()
    logging.info("Start jamming programmer")
    io_threads = IOManager()
    noiselib_thread = NoiseLib()

    # 主线程必须挂起，不能终止
    while True:
        string = input("Input Q to exit:")
        if string == "q" or string == "Q":
            break
        time.sleep(1)

    # 停止程序
    logging.info("Stop jamming programmer")
    io_threads.stop()
    noiselib_thread.stop()



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

    logging.info("Current log file {}".format(log_filepath))


if __name__ == "__main__":
    run()