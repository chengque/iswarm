import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot(id):
    data = pd.read_table("/home/chengque/workspace/Cfs"+id+".csv",sep=",")
    plt.figure()
    plt.plot(data['sz'],'r--')
    plt.plot(data['z'])
    plt.grid()
    plt.plot(data['vz'],'b--')
    plt.plot(data['svz'],'r')
    plt.plot(data['oz']/6000.0,'g')
    plt.legend(['sz','z','vz','vz*','thr'])



    plt.figure()
    plt.plot(data['sx'],'r--')
    plt.plot(data['x'])
    plt.grid()
    plt.plot(data['vx'],'b--')
    plt.plot(data['svx'],'r')
    plt.plot(data['ox']/30,'k')
    plt.legend(['sx','x','vx','vx*','ox'])


    plt.figure()
    plt.plot(data['sy'],'r--')
    plt.plot(data['y'])
    plt.grid()
    plt.plot(data['vz'],'b--')
    plt.plot(data['svz'],'r')
    plt.plot(data['oy']/30,'k')
    plt.legend(['sy','y','vy','vy*','oy'])

    plt.show()

if __name__=="__main__":
    plot(sys.argv[1])
