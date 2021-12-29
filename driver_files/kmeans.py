# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def kmeans_test(datalist,cluster_num):
    datalist = np.array(datalist)
    new_test = []
    for i in datalist:
        if i[1] < 4:
            new_test.append([i[0][0],i[0][1],0])
        else:
            new_test.append([i[0][0],i[0][1],1])

    X = np.array(new_test)
    # print(X)
    # print(X[0])
    # X = dataset
    color_list = [
        "blue",
        "green",
        "red",
        "cyan",
        "magenta",
        "yellow",
        "black",
]
    # %%
    from sklearn.cluster import KMeans
    # wcss_list = []
    # for cluster in range(1,11):
    #     kmeans = KMeans(n_clusters=cluster,init='k-means++',random_state=42)
    #     kmeans.fit(X)
    #     wcss_list.append(kmeans.inertia_)

    # print(wcss_list)


    # %%
    # plt.plot(range(1,11),wcss_list)
    # plt.show()

    # %%
    kmeans = KMeans(n_clusters=cluster_num,init='k-means++',random_state=42)
    y_pred = kmeans.fit_predict(X)
    # %%
    fig = plt.figure(figsize = (15,15))
    ax = fig.add_subplot(111, projection='3d')
    for i in range(cluster_num+1):
        ax.scatter(X[y_pred == i,0],X[y_pred == i,1],X[y_pred == i,2], s = 40 , color = color_list[i%len(color_list)])
        # plt.scatter(X[y_pred == 1,0],X[y_pred == 1,1],c='green')

    # plt.scatter(kmeans.cluster_centers_[:,0],kmeans.cluster_centers_[:,1],c='orange',s=100)
    plt.show()


