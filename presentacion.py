import cv2
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage import img_as_ubyte, img_as_float,color,measure
from matplotlib import pyplot as plt
import numpy as np
import scipy.ndimage

#path = "imagenes/c_198.jpeg"
path = "image/17.jpg"

#path = "GR/59.jpg"

#DENOISING IMAGE
img = img_as_float(cv2.imread(path))
sigma_est = np.mean(estimate_sigma(img, multichannel=True))
denoise_img = denoise_nl_means(img, h=1.15 * sigma_est, fast_mode=True, patch_size=5, patch_distance=3, multichannel=True)
denoise_8byte = img_as_ubyte(denoise_img)
img_8byte = img_as_ubyte(img)

#GRAY SCALE
gray = cv2.cvtColor(denoise_8byte,cv2.COLOR_BGR2GRAY)
#CONTRAST LIMITED ADAPTIVE HISTOGRAM EQUALIZATION => mejorar la imagen
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
clahe_cl1 = clahe.apply(gray)
#SEGMENTATION => THRESH_OTSU calcula el umbral
ret,thresh = cv2.threshold(clahe_cl1,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
#fill_hole = thresh.copy()
#thresh = scipy.ndimage.binary_fill_holes(thresh).astype(np.uint8)

kernel = np.ones((3,3)).astype(np.uint8)
#erose = cv2.erode(thresh,kernel,iterations=2)
#dilate = cv2.dilate(erose,kernel,iterations=2)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 1)# =  erose => dilate
opening = scipy.ndimage.binary_fill_holes(opening).astype(np.uint8)

sure_bg = cv2.dilate(opening,kernel,iterations=3)
#sure_bg = scipy.ndimage.binary_fill_holes(sure_bg).astype(np.uint8)

dist_transform_fill = cv2.distanceTransform(opening,cv2.DIST_L2,5)
ret2, sure_fg = cv2.threshold(dist_transform_fill,0.5*dist_transform_fill.max(),255,0)
#ret2, sure_fg = cv2.threshold(dist_transform_fill,0.35*dist_transform_fill.max(),255,0)
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)

ret3, markers = cv2.connectedComponents(sure_fg)
#markers = markers+10
markers2 = markers.copy()
# poner 1 donde hay cero, tal vez de error porque llegamos a 255 mas 1 => 0 dado que se paso los 8bits
# probar esa hipotesis
markers = markers+1
#markers[markers==0] = 1
markers[unknown==255] = 0
markers3 = markers.copy()

markers = cv2.watershed(img_8byte,markers)
markers4 = markers.copy()

#Let us color boundaries in yellow.
img_8byte[markers == -1] = [255,0,0]

img2 = color.label2rgb(markers, bg_label=1)
regions = measure.regionprops(markers)
print(len(regions))
titles = ['thresh','opening','sure_bg','sure_fg','d_transform_f','unknown','markers3','markers','img_8byte','img2']
#titles = ['unknown','markers','img_8byte','img2']
images = [thresh,opening,sure_bg,sure_fg,dist_transform_fill,unknown,markers3,markers,img_8byte,img2]
#images = [unknown,markers,img_8byte,img2]
for i in range(len(images)):
    plt.subplot(3,4, i+1)
    plt.imshow(images[i], 'gray')
    plt.title(titles[i])
    plt.xticks([])
    plt.yticks([])

plt.show()