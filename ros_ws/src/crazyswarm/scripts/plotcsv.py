import pandas as pd
import matplotlib.pyplot as plt


data = pd.read_table("Cfs0.csv",sep=",")
plt.figure()
plt.plot(data['z'])
plt.grid()
plt.plot(data['vz'],'b--')
plt.plot(data['svz'],'r')
plt.plot(data['oz']/6000.0,'g')
plt.legend(['z','vz','vz*','thr'])
plt.show()
