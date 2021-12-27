import pickle
import numpy as np
import math
import matplotlib.pyplot as plt
import kmeans

# print(new_list[1])

def makeRotation(base_lon,base_lat):
    def getXY(point,origin,angle):
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    lats = []
    lons = []

    for x in new_list:
        lonlat = x[2]
        for i in lonlat:
            lons.append(i[0][0])
            lats.append(i[0][1])


    new_lats = []
    new_lons = []

    for angle in range(0,360,30):
        for x,y in zip(lons,lats):
            nlo,nla = getXY((x,y),(base_lon,base_lat),math.radians(angle))
            new_lons.append(nlo)
            new_lats.append(nla)

    # print(new_lats)

    fin = []

    for x,y in zip(new_lons,new_lats):
        fin.append([x,y])

    import pickle
    with open('rotate.pkl','wb') as f:
        pickle.dump(fin,f)

    plt.scatter(new_lons,new_lats,s=1)
    plt.show()

with open('rotate.pkl','rb') as f:
    new_list = pickle.load(f)
kmeans.kmeans_test(new_list,10)