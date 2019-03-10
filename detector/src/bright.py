import Image
import os
import sys
import cv2

def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


directory = sys.argv[1]

for file_name in os.listdir(directory):
    print("Processing %s" % file_name)
    image = cv2.imread(os.path.join(directory, file_name))
    frame = increase_brightness(image, value=40)
    output_file_name = os.path.join(directory, file_name)
    cv2.imwrite(output_file_name, frame)

print("All done")
