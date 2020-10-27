import cv2
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage import img_as_ubyte, img_as_float,color,measure
from PIL import ImageTk, Image

from matplotlib import pyplot as plt
import numpy as np
import scipy.ndimage
YENNY = 0.30
class ProcesamientoImagen:
    def __init__(self, path):
        self.path = path

    def procesar(self):
        img = Image.open(self.path)
        #img = img_as_float(cv2.imread(self.path,cv2.IMREAD_UNCHANGED))
        img = img_as_float(img)
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
        ret2, sure_fg = cv2.threshold(dist_transform_fill, YENNY * dist_transform_fill.max(), 255, 0)
        # ret2, sure_fg = cv2.threshold(dist_transform_fill,0.35*dist_transform_fill.max(),255,0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        ret3, markers = cv2.connectedComponents(sure_fg)
        # markers = markers+10
        #markers = markers
        #markers = markers + 1
        markers[unknown == 255] = 0
        from skimage.segmentation import clear_border
        # opening = clear_border(opening)
        # markers = clear_border(markers)

        # img2 = cv2.applyColorMap(img_as_ubyte(unknown), cv2.COLORMAP_JET)
        markers = cv2.watershed(img_8byte, markers)
        img_8byte[markers == -1] = [255,0,0]
        # Let us color boundaries in yellow.
        regions = measure.regionprops(markers)

        return (img_8byte,regions)

    def showAllStep(self):
        # lectura de imagen
        if self.path is None: return
        original = Image.open(self.path)
        # Convierte una imagen a formato de punto flotante necesario para la eliminación de ruido.
        original_float = img_as_float(original)
        # Estima la desviación estándar de ruido en los canales de color de la imagen ruidosa
        out_estimate = estimate_sigma(original_float, multichannel=True)
        # np.mean calcula la media aritmética (promedio) de los datos (elementos de matriz) a lo largo del eje especificado.
        sigma_est = np.mean(out_estimate)
        # filtrando el ruido gaussiano mientras conserva los bordes y los detalles de las imágenes originales (filtro de medios no local)
        denoise_img = denoise_nl_means(original_float, h=1.15 * sigma_est, fast_mode=True, patch_size=5,
                                       patch_distance=3, multichannel=True)
        denoise_img = img_as_ubyte(denoise_img)

        # 2 mejorando la imagen
        # imagen sin ruido en escala de grises
        denoise_gray = cv2.cvtColor(denoise_img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl_img = clahe.apply(denoise_gray)

        # segmentando la imagen con el metodo de otsu
        ret, thresh = cv2.threshold(cl_img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        fill_hole = scipy.ndimage.binary_fill_holes(thresh).astype(np.uint8)

        # noise removal
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        opening = scipy.ndimage.binary_fill_holes(opening).astype(np.uint8)

        # sure background area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret, sure_fg = cv2.threshold(dist_transform, YENNY * dist_transform.max(), 255, 0)

        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        # Marker labelling
        ret, markers = cv2.connectedComponents(sure_fg)

        # Add one to all labels so that sure background is not 0, but 1
        #markers = markers + 1

        # Now, mark the region of unknown with zero
        markers[unknown == 255] = 0

        markers = cv2.watershed(denoise_img, markers)
        denoise_img[markers == -1] = [255, 0, 0]

        img2 = color.label2rgb(markers, bg_label=1)
        regions = measure.regionprops(markers)
        print("total de elemento encontrados: ", len(regions))
        titles = ['original gray', 'clahe', 'thresh', 'opening', 'sure_bg', 'dist_transform', 'denoise_img', 'label']
        images = [denoise_gray, cl_img, thresh, opening, sure_bg, dist_transform, denoise_img, img2]

        for i in range(len(images)):
            plt.subplot(2, 4, i + 1)
            plt.imshow(images[i], 'gray')
            plt.title(titles[i])
            plt.xticks([])
            plt.yticks([])
        plt.show()


