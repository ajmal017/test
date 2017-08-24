
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

strike = np.linspace(50,150,24)
ttm = np.linspace(0.5,2.5,24)
strike, ttm = np.meshgrid(strike, ttm)

iv = (strike - 100) ** 2 / (100 * strike) / ttm
fig = plt.figure(figsize=(9,6))
ax = fig.gca(projection='3d')

surf = ax.plot_surface(strike, ttm, iv, rstride=2, cstride=2,
                       cmap=plt.cm.coolwarm, linewidth=0.5,
                       antialiased=True)

ax.set_xlabel('strike')
ax.set_ylabel('time-to-maturity')
ax.set_zlabel('implied volatility')

fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()