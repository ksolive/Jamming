import queue
import threading
import numpy as np

read_data = queue.Queue(100)
write_data = queue.Queue(100)
send_data = queue.Queue(100) # ANC降噪后片段，ASR读取

mutex_noise = threading.Lock()

run_time = 0  # 运行时间
tmp_x = np.array([])
tmp_y = np.array([])

tmp = np.array([])

is_jamming = True #ASR识别结果，识别到时改为False，由指令重放部分改回
keyword_cache = np.array([]) #ASR识别为指令的部分，指令重放部分读取
lock_ars = threading.Lock() #ASR锁，防止竞争修改 is_jamming