from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score, calinski_harabaz_score
import matplotlib.pyplot as plot
import matplotlib.cm as cm
import numpy as np
from itertools import cycle
from random import randint
from sklearn.cluster import DBSCAN
import pandas as pd

__author__ ='SebastiÃ¡n M. Palacio'

def find_min_distances(X1, X2):
    min_dist = np.zeros(len(X1))

    for i, x1 in enumerate(X1):
        dists = np.sqrt(np.sum((X2 - x1) ** 2, axis=1))
        min_dist[i] = dists.min()

    return min_dist

def split_data_random(X, split_size):
    # copy data
    XC = np.copy(X)

    # split
    lo = randint(1, len(X) - split_size) - 1
    up = lo + split_size
    XSP = XC[lo:up:1]

    # remaining
    XRE = np.delete(XC, np.s_[lo:up:1], 0)
    return (XSP, XRE)

def expl_hopkins(X, split_size = 50, num_iters = 10):
    seed = 0
    np.random.seed(seed)
    n, d = X.shape  # obtenemos int de la dimensión de x
    m = np.zeros((n, d))

    XR = np.random.random((n, d))

    print("calculating hopkins stats to detect if the data set has clusters...")

    hopkins_stats = []

    for i in range(0, num_iters):
        (X_spl, X_tra) = split_data_random(X, split_size)
        (X_ran, X_rem) = split_data_random(XR, split_size)

        min_dist_ran = find_min_distances(X_ran, X_tra)
        min_dist_spl = find_min_distances(X_spl, X_tra)

        # print("random")
        # print min_dist_ran
        ran_sum = min_dist_ran.sum()
        # print("sum %.3f" % (ran_sum))

        # print("split")
        # print min_dist_spl
        spl_sum = min_dist_spl.sum()
        # print("sum %.3f" % (spl_sum))

        hopkins_stat = spl_sum / (ran_sum + spl_sum)
        print("hopkins stats %.3f" % (hopkins_stat))
        hopkins_stats.append(hopkins_stat)

    av_hopkins_stat = np.mean(hopkins_stats)
    print("average hopkins stat %.3f" % (av_hopkins_stat))

def cluster_internal_validation(X, n_clusters, model=None):
    lscores = []

    for nc in range(2, n_clusters + 1):
        print(nc)
        if model is None:
            km = KMeans(n_clusters=nc, random_state=10)
        else:
            km = DBSCAN(eps=0.5, min_samples=10, leaf_size=30, n_jobs=-1)

        labels = km.fit_predict(X)
        lscores.append((
            silhouette_score(X, labels),
            calinski_harabaz_score(X, labels)
        ))

    print(lscores)
    fig = plot.figure(figsize=(15, 5))
    ax = fig.add_subplot(121)
    plot.plot(range(2, n_clusters + 1), [x for x, _  in lscores])
    plot.title('Silhoutte Score')
    plot.xlabel('Number of Clusters')
    ax = fig.add_subplot(122)
    plot.plot(range(2, n_clusters + 1), [x for _, x in lscores])
    plot.title('Calinski-Harabaz Score')
    plot.xlabel('Number of Clusters')
    plot.show()



def silhouette_coef(X, range_n_clusters, model=None):

    for n_clusters in range_n_clusters:

        #Create a subplot wtih 1 row and 2 cols
        fig, (ax1, ax2) = plot.subplots(1, 2)
        fig.set_size_inches(18, 7)

        #Primer Subplot: Silhouette plot con rango x [-1,1] y rango y [0, len(X)] pero le agregamos un espacio en blanco (n_clusters+1)*10
        ax1.set_xlim([-1, 1])
        ax1.set_ylim([0, len(X) + (n_clusters + 1)* 10])

        #modelo de cluster
        if model is None:
            clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        else:
            clusterer = DBSCAN(eps=range_n_clusters, min_samples=200, leaf_size=30, n_jobs=-1)
        cluster_labels = clusterer.fit_predict(X)

        #Silhoutte score average for all samples
        silhouette_avg = silhouette_score(X, cluster_labels)
        print('For n_clusters = ', n_clusters, ' The average SC is: ', silhouette_avg)

        #Silhoutte score for each sample
        sample_silhouette_values = silhouette_samples(X, cluster_labels)


        y_lower = 10
        #Agregando los SC para los samples por cluster i y ordenarlos
        for i in range(n_clusters):
            ith_cluster_sc_values = sample_silhouette_values[cluster_labels == i]
            ith_cluster_sc_values.sort()

            size_cluster_i = ith_cluster_sc_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.spectral(float(i) / n_clusters)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                          0, ith_cluster_sc_values,
                          facecolor=color, edgecolor=color, alpha=0.7)

            #Le ponemos el nombre del cluster en el grÃ¡fico
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        #2do Plot: Mostramos los verdaderos clusters formados
        colors = cm.spectral(cluster_labels.astype(float) / n_clusters)
        ax2.scatter(X[:, 0], X[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                    c=colors)

        #Ponemos nombre al cluster
        centers = clusterer.cluster_centers_

        #Dibujamos el centro con un cÃ­ruclo
        ax2.scatter(centers[:, 0], centers[:, 1],
                    marker='o', c="white", alpha=1, s=200)

        for i, c in enumerate(centers):
            ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1, s=50)

        ax2.set_title("The visualization of the clustered data.")
        ax2.set_xlabel("Feature space for the 1st feature")
        ax2.set_ylabel("Feature space for the 2nd feature")

        plot.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                      "with n_clusters = %d" % n_clusters),
                     fontsize=14, fontweight='bold')

        plot.show()

def kmeans_plus_plus(X, k, n_init, max_iter, show_plot = True, drop='total_code'):
    '''
    :param X:
    :param k: number_clusters
    :param n_init: Number of time the k-means algorithm will be run with different centroid seeds
    :param max_iter:Maximum number of iterations of the k-means algorithm for a single run
    :return:
    '''
    kmeans = KMeans(init='k-means++', n_clusters=k, n_init=n_init, max_iter=max_iter, random_state=0).fit(
        X.drop(drop, axis=1))

    labels = kmeans.labels_
    cluster_centers = kmeans.cluster_centers_
    df = pd.DataFrame(labels, columns=['labels'])
    df = pd.concat([X, df], axis=1)
    df = df.copy()
    df.to_csv('clusters.csv', sep=';', index=False, encoding='latin1')
    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)
    X = X.drop(drop, axis=1).values
    if show_plot:
        plot.figure(1)
        plot.clf()

        colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
        for k, col in zip(range(n_clusters_), colors):
            my_members = labels == k
            cluster_center = cluster_centers[k]
            plot.plot(X[my_members, 0], X[my_members, 1], col + '.')
            plot.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                     markeredgecolor='k', markersize=14)
        plot.title('Estimated number of clusters: %d' % n_clusters_)
        plot.show()











