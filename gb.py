import cv2
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage import img_as_ubyte, img_as_float,color,measure
from matplotlib import pyplot as plt
import numpy as np
import scipy.ndimage

class ProcesamientoImagen:
    def __init__(self, path):
        self.path = path

    def procesar(self):
        img = img_as_float(cv2.imread(self.path))
        sigma_est = np.mean(estimate_sigma(img, multichannel=True))
        denoise_img = denoise_nl_means(img, h=1.15 * sigma_est, fast_mode=True, patch_size=5, patch_distance=3,
                                       multichannel=True)
        denoise_8byte = img_as_ubyte(denoise_img)
        img_8byte = img_as_ubyte(img)
        # GRAY SCALE
        gray = cv2.cvtColor(denoise_8byte, cv2.COLOR_BGR2GRAY)
        # CONTRAST LIMITED ADAPTIVE HISTOGRAM EQUALIZATION => mejorar la imagen
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_cl1 = clahe.apply(gray)
        # SEGMENTATION => THRESH_OTSU calcula el umbral
        ret, thresh = cv2.threshold(clahe_cl1, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        # fill_hole = thresh.copy()
        # umbral  => print(ret)
        kernel = np.ones((3, 3)).astype(np.uint8)
        # erose = cv2.erode(thresh,kernel,iterations=1)
        # dilate = cv2.dilate(erose,kernel,iterations=1)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)  # =  erose => dilate
        opening = scipy.ndimage.binary_fill_holes(opening).astype(np.uint8)

        # from skimage.segmentation import clear_border
        # opening = clear_border(opening)
        # from skimage.segmentation import clear_border
        # clear_b = clear_border(thresh)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
        # dist_transform_fill = cv2.distanceTransform(fill_hole,cv2.DIST_L2,5)
        dist_transform_fill = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret2, sure_fg = cv2.threshold(dist_transform_fill, 0.5 * dist_transform_fill.max(), 255, 0)
        # ret2, sure_fg = cv2.threshold(dist_transform_fill,0.35*dist_transform_fill.max(),255,0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        ret3, markers = cv2.connectedComponents(sure_fg)
        # markers = markers+10
        markers = markers
        markers[unknown == 255] = 0
        from skimage.segmentation import clear_border
        # opening = clear_border(opening)
        # markers = clear_border(markers)

        # img2 = cv2.applyColorMap(img_as_ubyte(unknown), cv2.COLORMAP_JET)
        markers = cv2.watershed(img_8byte, markers)
        # Let us color boundaries in yellow.
        regions = measure.regionprops(markers)
        img_8byte[markers == -1] = [255,0,0]

        return (img_8byte,regions)


