import cv2
import numpy as np
import matplotlib.pyplot as plt

path = 'Resources/Grapes2.png'
image = cv2.imread(path)
original = image.copy()
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

pixel_values = image.reshape((-1,3))
pixel_values = np.float32(pixel_values)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 9, 0.2)

# number of clusters (K)
k = 5
_, labels, (centers) = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

# convert back to 8 bit values
centers = np.uint8(centers)

# flatten the labels array
labels = labels.flatten()

# convert all pixels to the color of the centroids
segmented_image = centers[labels.flatten()]

# reshape back to the original image dimension
segmented_image = segmented_image.reshape(image.shape)

# disable only the cluster number 2 (turn the pixel into black)
masked_image = np.copy(image)
# convert to the shape of a vector of pixel values
masked_image = masked_image.reshape((-1, 3))
# color (i.e cluster) to disable
cluster1 = 1
cluster2 = 2
cluster3 = 3
cluster4 = 4
cluster5 = 5
print(labels)
#masked_image[labels == cluster1] = [0, 0, 0]
#masked_image[labels == cluster2] = [0, 0, 0]
masked_image[labels == cluster3] = [0, 0, 0]
#masked_image[labels == cluster4] = [0, 0, 0]
masked_image[labels == cluster5] = [0, 0 ,0]
# convert back to original shape
masked_image = masked_image.reshape(image.shape)
# show the image

lower_green = np.array([0,100,0])
upper_green = np.array([200,255,50])

mask = cv2.inRange(masked_image, lower_green, upper_green)
M_I = np.copy(masked_image)
M_I[mask == 0] = [0,0,0]

res = cv2.bitwise_and(original, original, mask = mask)

fig, axs = plt.subplots(2)
axs[0].imshow(res)
axs[1].imshow(original)

plt.show()
