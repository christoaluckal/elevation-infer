import pickle
import numpy as np
import math
import matplotlib.pyplot as plt
import kmeans
from random import randint as rd
# print(new_list[1])

lat_factor = 0.000591
lon_factor = 74.150652-74.152006
ele_factor = 0.75

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

# with open('rotate.pkl','rb') as f:
#     new_list = pickle.load(f)
# kmeans.kmeans_test(new_list,10)

def write_new():
    with open('buildings.pkl','rb') as bld:
        bld_list = pickle.load(bld)

    t_list = []

    for i in range(500):
        sample = bld_list[rd(0,4)]
        sample0 = np.array(sample[0])
        sample1 = np.array(sample[1])
        sample2 = np.array(sample[2])
        factor_val_x = rd(-500,500)
        factor_val_y = rd(-500,500)
        ele_rand = rd(0,10)
        sample0 = sample0 + [factor_val_x*lon_factor,factor_val_y*lat_factor]
        sample1 = sample1*ele_factor*ele_rand
        sample2 =sample2 + [factor_val_x*lon_factor,factor_val_y*lat_factor]
        
        t_list.append([sample0,sample1,sample2])


    with open('translates.pkl','wb') as f:
        pickle.dump(t_list,f)

def clust():
    tt_list = []
    with open('translates.pkl','rb') as g:
        tt_list = pickle.load(g)

    kmeans.kmeans_test(tt_list,2)

# write_new()
clust()