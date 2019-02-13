# import the necessary packages
import argparse
from skimage.measure import compare_ssim as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2

def compare_images(imageA, imageB, title):
	# compute the mean squared error and structural similarity
	# index for the images
	s,diff = ssim(imageA, imageB, full=True)

	# setup the figure
	fig = plt.figure(title)
	plt.suptitle("SSIM: {}".format(s))

	# show first image
	ax = fig.add_subplot(1, 2, 1)
	plt.imshow(imageA, cmap = plt.cm.gray)
	plt.axis("off")

	# show the second image
	ax = fig.add_subplot(1, 2, 2)
	plt.imshow(imageB, cmap = plt.cm.gray)
	plt.axis("off")

	# show the images
	plt.show()

ap = argparse.ArgumentParser()
ap.add_argument("-a", "--img_a", required=True, help="path to 1st image")
ap.add_argument("-b", "--img_b", required=True, help="path to 2nd image")
ap.add_argument("-c", "--img_c", required=True, help="path to 3rd image")
args = vars(ap.parse_args())

original = cv2.imread(args['img_a'])
contrast = cv2.imread(args['img_b'])
shopped = cv2.imread(args['img_c'])

original = cv2.resize(original, (250, 250))
contrast = cv2.resize(contrast, (250,250))
shopped = cv2.resize(shopped, (250,250))

# convert the images to grayscale
original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
shopped = cv2.cvtColor(shopped, cv2.COLOR_BGR2GRAY)

# initialize the figure
fig = plt.figure("Images")
images = ("img1", original), ("img2", contrast), ("img3", shopped)

# loop over the images
for (i, (name, image)) in enumerate(images):
	# show the image
	ax = fig.add_subplot(1, 3, i + 1)
	ax.set_title(name)
	plt.imshow(image, cmap = plt.cm.gray)
	plt.axis("off")

# show the figure
plt.show()

# compare the images
compare_images(original, contrast, "Img1 vs. Img2")
compare_images(original, shopped, "Img1 vs. Img3")
compare_images(contrast, shopped, "Img2 vs. Img3")


