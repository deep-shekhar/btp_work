from sklearn.cluster import KMeans
from collections import OrderedDict
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math 
from datetime import datetime

def dist(labA, labB):
	deltaL = labA[0] - labB[0]
	deltaA = labA[1] - labB[1]
	deltaB = labA[2] - labB[2]
	c1 = math.sqrt(labA[1] * labA[1] + labA[2] * labA[2])
	c2 = math.sqrt(labB[1] * labB[1] + labB[2] * labB[2])
	deltaC = c1 - c2
	deltaH = deltaA * deltaA + deltaB * deltaB - deltaC * deltaC
	deltaH = 0 if deltaH < 0 else math.sqrt(deltaH)
	sc = 1.0 + 0.045 * c1
	sh = 1.0 + 0.015 * c1
	deltaLKlsl = deltaL / (1.0)
	deltaCkcsc = deltaC / (sc)
	deltaHkhsh = deltaH / (sh)
	i = deltaLKlsl * deltaLKlsl + deltaCkcsc * deltaCkcsc + deltaHkhsh * deltaHkhsh
	return 0 if i < 0 else math.sqrt(i)


def rgb2lab (inputColor):
	num = 0
	RGB = [0, 0, 0]

	for value in inputColor :
	   value = float(value) / 255

	   if value > 0.04045 :
		   value = ( ( value + 0.055 ) / 1.055 ) ** 2.4
	   else :
		   value = value / 12.92

	   RGB[num] = value * 100
	   num = num + 1

	XYZ = [0, 0, 0,]

	X = RGB [0] * 0.4124 + RGB [1] * 0.3576 + RGB [2] * 0.1805
	Y = RGB [0] * 0.2126 + RGB [1] * 0.7152 + RGB [2] * 0.0722
	Z = RGB [0] * 0.0193 + RGB [1] * 0.1192 + RGB [2] * 0.9505
	XYZ[ 0 ] = round( X, 4 )
	XYZ[ 1 ] = round( Y, 4 )
	XYZ[ 2 ] = round( Z, 4 )

	XYZ[ 0 ] = float( XYZ[ 0 ] ) / 95.047         
	XYZ[ 1 ] = float( XYZ[ 1 ] ) / 100.0         
	XYZ[ 2 ] = float( XYZ[ 2 ] ) / 108.883    

	num = 0
	for value in XYZ :

	   if value > 0.008856 :
		   value = value ** ( 0.3333333333333333 )
	   else :
		   value = ( 7.787 * value ) + ( 16 / 116 )

	   XYZ[num] = value
	   num = num + 1

	Lab = [0, 0, 0]

	L = ( 116 * XYZ[ 1 ] ) - 16
	a = 500 * ( XYZ[ 0 ] - XYZ[ 1 ] )
	b = 200 * ( XYZ[ 1 ] - XYZ[ 2 ] )

	Lab [ 0 ] = round( L, 5 )
	Lab [ 1 ] = round( a, 5 )
	Lab [ 2 ] = round( b, 5 )

	return Lab
 
class ColorLabeler:

	def __init__(self):
		colors = OrderedDict({
			"red": (255, 0, 0),
			"green": (0, 255, 0),
			"blue": (0, 0, 255)})
		self.lab = np.zeros((len(colors), 1, 3))
		self.colorNames = []
 
		for (i, (name, rgb)) in enumerate(colors.items()):
			self.lab[i] = rgb2lab(rgb)
			self.colorNames.append(name)
		print(self.lab)

	def label(self,orig_img,x1,y1,x2,y2,req_color):
			img = orig_img[y1:y2, x1:x2]
			#img = cv2.GaussianBlur(img, (5, 5), 0)
			height, width, dim = img.shape
			
			img_vec = np.reshape(img, [height * width, dim] )
			kmeans = KMeans(n_clusters=3)
			kmeans.fit( img_vec )

			unique_l, counts_l = np.unique(kmeans.labels_, return_counts=True)
			sort_ix = np.argsort(counts_l)
			sort_ix = sort_ix[::-1]

			'''fig = plt.figure()
			ax = fig.add_subplot(111)
			x_from = 0.05
			
			for cluster_center in kmeans.cluster_centers_[sort_ix]:
				print(cluster_center[2], cluster_center[1], cluster_center[0])
				if abs(max(cluster_center)-min(cluster_center)) < 20:
					print('not rgb diff= {} '.format(abs(max(cluster_center)-min(cluster_center))))
					continue 		
				ax.add_patch(patches.Rectangle( (x_from, 0.05), 0.29, 0.9, alpha=None,
						                        facecolor='#%02x%02x%02x' % (cluster_center[2], cluster_center[1], cluster_center[0] ) ) )
				x_from = x_from + 0.31

			plt.show()
			'''
			
			obj_lab = np.zeros((1, 1, 3))
			
			for cluster_center in kmeans.cluster_centers_[sort_ix]:
				if abs(max(cluster_center)-min(cluster_center)) > 35:
					#print('not rgb diff= {} '.format(abs(max(cluster_center)-min(cluster_center))))
					obj_lab = rgb2lab((cluster_center[2], cluster_center[1], cluster_center[0]))
					break
					
			minDist = np.inf
	 		color_idx = -1
			print(obj_lab)
			# loop over the known L*a*b* color values
			for (i, row) in enumerate(self.lab):
				d = abs(row[0][0] - obj_lab[0]) + abs(row[0][1] - obj_lab[1]) + abs(row[0][2] - obj_lab[2])
				if d < minDist:
					minDist = d
					color_idx = i
				print('distance from {} is {} color = {}, min={}'.format(i,d,self.colorNames[i],minDist))
	 			
			if self.colorNames[color_idx] == req_color:
				print('req_color was = {}'.format(req_color))
				cv2.imwrite("detect_result{}.png".format(datetime.now()),orig_img)
				return 1

			return 0
			
	


