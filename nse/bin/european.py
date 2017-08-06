#European call options Inner value plot
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['font.family'] = 'serif'

#Option Strike
K = 8000
#Graphical Output
S = np.linspace(7000,9000,5) #index level values
h = np.maximum(S - K,0)

plt.figure()
plt.plot(S, h , lw=2.5)
plt.xlabel('index level $S_t$ at maturity')
plt.ylabel('inner value of European call option')
plt.grid(True)
plt.show()