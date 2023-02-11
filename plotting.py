import matplotlib.pyplot as plt
import numpy as np


tpt = [0.99345, 0.99188, 0.99333]
latency = [1.00631, 1.00639, 1.00644]
x_axis = np.array([5, 10, 20])
fig, ax = plt.subplots(1, 2, figsize=(10, 5))
ax[0].bar(x_axis, latency, label="latency")
ax[1].bar(x_axis, tpt, label="throughput")
ax[0].legend()
ax[1].legend()
plt.show()



