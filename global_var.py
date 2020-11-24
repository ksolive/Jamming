import queue
import threading
import numpy as np

read_data = queue.Queue(100)
write_data = queue.Queue(100)

mutex_noise = threading.Lock()

run_time = 0  # 运行时间
tmp_x = np.array([])
tmp_y = np.array([])

tmp = np.array([])