import pandas as pd
import matplotlib.pyplot as plt
import sys

def plot(id):
    data = pd.read_table("/home/chengque/workspace/Cfs"+id+".csv",sep=",")
    t=data['t'].values
    print t
    plt.figure()
    plt.plot(t,data['sz'],'r--')
    plt.plot(t,data['z'])
    plt.grid()
    plt.plot(t,data['vz'],'b--')
    plt.plot(t,data['svz'],'r')
    plt.plot(t,data['oz']/6000.0,'g')
    plt.legend(['sz','z','vz','vz*','thr'],loc = 'lower right')



    plt.figure()
    plt.plot(t,data['sx'],'r--')
    plt.plot(t,data['x'])
    plt.grid()
    plt.plot(t,data['vx'],'b--')
    plt.plot(t,data['svx'],'r')
    plt.plot(t,data['oy']/10,'k')
    print data['oy'].values
    pitch=data['ey'].values
    #print pitch
    #print len(pitch)
    for i in range(len(pitch)):
        if(pitch[i]>2):
            pitch[i]=3.14-pitch[i]
        if(pitch[i]<-2):
            pitch[i]=3.14+pitch[i]
    plt.plot(t,pitch*5.73,'k--')
    plt.legend(['sx','x','vx','vx*','ox','ex'],loc = 'lower right')


    plt.figure()
    plt.plot(t,data['sy'],'r--')
    plt.plot(t,data['y'])
    plt.grid()
    plt.plot(t,data['vy'],'b--')
    plt.plot(t,data['svy'],'r')
    plt.plot(t,data['ox']/10,'k')
    pitch=data['ex'].values
    for i in range(len(pitch)):
        if(pitch[i]>2):
            pitch[i]=3.14-pitch[i]
        if(pitch[i]<-2):
            pitch[i]=3.14+pitch[i]
    plt.plot(t,pitch*5.73,'k--')
    plt.legend(['sy','y','vy','vy*','oy','ey'],loc = 'lower right')

    plt.show()

if __name__=="__main__":
    plot(sys.argv[1])
