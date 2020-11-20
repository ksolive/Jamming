import threading,time,os,logging
import wave

class NoiseLib(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        # 读取噪声Pairs
        self.exit_flag = False
        while not self.exit_flag:
            print("*")
            time.sleep(5)

    def stop(self):
        self.exit_flag = True
        self.join()

    def load_noise_pairs(self):
        # 获取raw目录下所有音频文件名
        raw_noise_filenames = []
        raw_noise_dir = os.path.join("waves","raw")
        distort_noise_dir = os.path.join("waves","distort")
        for root,dirs,files in os.walk(raw_noise_dir):  # r字符串前+r表示不含转义字符
            for file in files:
                raw_noise_filenames.append(file)
        try:
            for filename in raw_noise_filenames:
                wf1 = wave.open(os.path.join(raw_noise_dir,filename),"rb")
                wf2 = wave.open(os.path.join(distort_noise_dir,filename),"rb")
        except:
            logging.info("Can't find noise file pairs")
            raise TypeError()

        data = wf1.readframes(1000)
        

    @classmethod
    def get_noise_clip(cls):
        return "***"