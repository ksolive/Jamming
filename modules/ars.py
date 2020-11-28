import global_var
import settings
import threading
import ctypes


class ASRManager(object):
    def __init__(self):
        super(ASRManager, self).__init__()
        self.asr_threads=[]
        self.c = ctypes.CDLL("ASR.dll")

    def create_asr_thread(self):
        asr_thread = asr_thread()
        asr_thread.run()
        self.asr_threads.append(asr_thread)

    def kill_all(self):
        for asr_thread in self.asr_threads:
            asr_thread.stop()
            asr_threads.remove(asr_thread)


class asr_thread(threading.Thread):
    def __init__(self):
        super(asr_thread, self).__init__()

    def run(self):
        # 获取声音片段
        sound = global_var.send_data.get()
        # 数据类型转换：float ndarray->（C）void*
        sound.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p))
        # 调用c中函数，返回值为c中true和false，在python中是0，1
        back=ASRManager.c.function(sound)
        if(back != 0):
            global_var.lock_ars.acquire()
            global_var.is_jamming=False
            global_var.keyword_cache=sound
            global_var.lock_ars.release()
            print("success")
        print("run")

    
    def stop(self):
        self.__flag.set()    # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()    # 设置为False 
    '''
    def stop(self):
        print("stop")
    '''

        