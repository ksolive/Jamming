import numpy as np

a = np.random.randint(0,16,size=(10))
print(a)

b = a.astype(np.int16).tobytes()

print(b)

c = b.decode(encoding="utf-8")

print(c)