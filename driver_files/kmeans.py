# %%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def kmeans_test(datalist,cluster_num):
    dataset = np.array(datalist)
    X = dataset
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
    for i in range(cluster_num+1):
        plt.scatter(X[y_pred == i,0],X[y_pred == i,1],c=color_list[(i%len(color_list))])
        # plt.scatter(X[y_pred == 1,0],X[y_pred == 1,1],c='green')

    plt.scatter(kmeans.cluster_centers_[:,0],kmeans.cluster_centers_[:,1],c='orange',s=100)
    plt.show()


