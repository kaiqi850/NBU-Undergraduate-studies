import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.cluster import KMeans
import utilities

# Load data
# data_label是标签，在这里没用
data,data_label = utilities.load_data('data_multivar.txt')
x = data[:,0]
y = data[:,1]


# # Plot data
plt.figure()
plt.scatter(x, y, marker='o',facecolors='none', edgecolors='k', s=30)
x_min, x_max = min(x) - 1, max(x) + 1
y_min, y_max = min(y) - 1, max(y) + 1
plt.title('Input data')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.show()

# # Train the model
num_clusters = 4
kmeans = KMeans(init='k-means++', n_clusters=num_clusters, n_init=10)
kmeans.fit(data)


plt.figure()
plt.clf()
plt.scatter(x, y, marker='o', 
        facecolors='none', edgecolors='k', s=30)
# 得到质心点
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:,0], centroids[:,1], marker='o', s=100, linewidths=3,
        color='k', zorder=10, facecolors='red')
x_min, x_max = min(x) - 1, max(x) + 1
y_min, y_max = min(y) - 1, max(y) + 1

plt.title('Centoids obtained using KMeans')
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())


# Step size of the mesh
step_size = 0.1
# Plot the boundaries
x_min, x_max = min(x) - 1, max(x) + 1
y_min, y_max = min(y) - 1, max(y) + 1
x_values, y_values = np.meshgrid(np.arange(x_min, x_max, step_size), np.arange(y_min, y_max, step_size))

# Predict labels for all points in the mesh
predicted_labels = kmeans.predict(np.c_[x_values.ravel(), y_values.ravel()])

# Plot the results
predicted_labels = predicted_labels.reshape(x_values.shape)

plt.imshow(predicted_labels, interpolation='nearest',
           extent=(x_values.min(), x_values.max(), y_values.min(), y_values.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')
plt.show()
