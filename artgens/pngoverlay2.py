#--------------------------------------------------------------------------------
# Overlay transparent PNG files with OpenCV
#
# https://gist.github.com/electricbaka/05fae17e598d2500c2b240919217cd65
#
# import cv2
# from pngoverlay import PNGOverlay
#
# (1) read the background
# dst = cv2.imread('background.jpg') 
#
# (2) read the image
# fish = PNGOverlay('img_fish.png')
#
# (3)show the image
# fish.show(dst, x, y) #dst is the background image you want to display. x and y are the center coordinates you want to display the overlayed object
#
#
# ---------- methods available to this class  ----------
# Rotate object
# fish.rotate(45) # 45 degree。
#
# Resize object
# fish.resize(0.5) # half size
#--------------------------------------------------------------------------------

import cv2
import numpy as np

class PNGOverlay():
    def __init__(self, filename):
        # Import as an image with alpha channel (BGRA)
        self.src_init = cv2.imread(filename, -1)
        self.src_init = cv2.cvtColor(self.src_init, cv2.COLOR_BGRA2RGBA)
        
        #Add the minimum required transparent color image to the surroundings
        self.src_init = self._addTransparentImage(self.src_init)

        #Image transformation does not require default
        self.flag_transformImage = False

        #Preprocess the image
        self._preProcessingImage(self.src_init)

        #initial value
        self.degree = 0
        self.size_value = 1

    def _addTransparentImage(self, src): #Add a transparent color area of ​​the image to the surroundings in advance so as not to crop when rotating
        height, width, _ = src.shape # Obtaining HWC

        #Makes a transparent square with a diagonal length as one side for rotation
        diagonal = int(np.sqrt(width **2 + height ** 2))
        src_diagonal = np.zeros((diagonal, diagonal, 4), dtype=np.uint8)

        #Overwrite src in the center of the transparent square
        p1 = int(diagonal/2 - width/2)
        p2 = p1 + width
        q1 = int(diagonal/2 - height/2)
        q2 = q1 + height
        src_diagonal[q1:q2,p1:p2,:] = src[:,:,:]

        return src_diagonal

    def _preProcessingImage(self, src_bgra): #Divide the BGRA image into a BGR image (src) and an A image (mask), and retain the information required for overlaying
        self.mask = src_bgra[:,:,3]  # Extract only A from src and use it as a mask
        self.src = src_bgra[:,:,:3]  # Extract only GBR from src and use it as src
        self.mask = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2BGR)  # A into 3 channels
        self.mask = self.mask / 255.0  # Normalized to 0.0-1.0
        self.height, self.width, _ = src_bgra.shape # Obtaining HWC
        self.flag_preProcessingImage = False #Lower the preprocessing flag once

    def rotate(self, degree): #Image rotation parameter reception
        self.degree = degree
        self.flag_transformImage = True

    def resize(self, size_value): #Image size parameter reception
        self.size_value = size_value
        self.flag_transformImage = True

    def _transformImage(self): #It is necessary to resize and rotate in a series at once instead of doing it separately in each method
        #---------------------------------
        #resize
        #---------------------------------
        self.src_bgra = cv2.resize(self.src_init, dsize=None, fx=self.size_value, fy=self.size_value) #Specified by magnification

        #re-read into height and width from the new size
        self.height, self.width, _ = self.src_bgra.shape # Obtaining HWC

        #---------------------------------
        #rotate
        #---------------------------------
        #getRotationMatrix2D
        center = (int(self.width/2), int(self.height/2))
        trans = cv2.getRotationMatrix2D(center, self.degree, 1)

        #Affine transformation
        self.src_bgra = cv2.warpAffine(self.src_bgra, trans, (self.width, self.height))

        #Since the transformation is finished, set the flag to False
        self.flag_transformImage == False

        #Preprocess the image before overlaying
        self.flag_preProcessingImage = True

    def show(self, dst, x, y): #src is superimposed on the dst image and displayed. Center coordinate specification
        #Rotation and resizing need to be done in bulk just before overlay
        if self.flag_transformImage == True:
            self._transformImage()

        #Execute if preprocessing is required
        if self.flag_preProcessingImage == True:
            self._preProcessingImage(self.src_bgra)

        x1, y1 = x - int(self.width/2), y - int(self.height/2)
        x2, y2 = x1 + self.width, y1 + self.height #Note that if you do not use a calculation formula that adds width and height, an error may occur with a deviation of 1.
        a1, b1 = 0, 0
        a2, b2 = self.width, self.height
        dst_height, dst_width, _ = dst.shape

        #Not displayed if the x and y specified coordinates are completely out of dst
        if x2 <= 0 or x1 >= dst_width or y2 <= 0 or y1 >= dst_height:
            return

        #Corrects the protrusion from the dst frame
        x1, y1, x2, y2, a1, b1, a2, b2 = self._correctionOutofImage(dst, x1, y1, x2, y2, a1, b1, a2, b2)

        # Blend src images to dst by a percentage of A
        dst[y1:y2, x1:x2] = self.src[b1:b2, a1:a2] * self.mask[b1:b2, a1:a2] + dst[y1:y2, x1:x2] * ( 1 - self.mask[b1:b2, a1:a2] )

    def _correctionOutofImage(self, dst, x1, y1, x2, y2, a1, b1, a2, b2): #Correct x, y and a, b if the x, y coordinates are out of frame
        dst_height, dst_width, _ = dst.shape
        if x1 < 0:
            a1 = -x1
            x1 = 0
        if x2 > dst_width:
            a2 = self.width - x2 + dst_width
            x2 = dst_width
        if y1 < 0:
            b1 = -y1
            y1 = 0
        if y2 > dst_height:
            b2 = self.height - y2 + dst_height
            y2 = dst_height

        return x1, y1, x2, y2, a1, b1, a2, b2

#Test code
if __name__ == '__main__':
    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)

    #Instance generation
    happy = PNGOverlay('/mnt/c/linuxmirror/14131.png')
    sad = PNGOverlay('/mnt/c/linuxmirror/14133.png')
    test = PNGOverlay('/mnt/c/linuxmirror/14134.png')
    kurage = PNGOverlay('/mnt/c/linuxmirror/14149.png')

    #Overlay method execution
    happy.show(dst, 200, 100)
    sad.show(dst, 500, 800)
    test.show(dst, 800, 500)
    kurage.resize(0.8)
    kurage.rotate(40)
    kurage.show(dst, 400, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate1.jpg', dst)  
#    cv2.imshow('dst',dst)
    cv2.waitKey(0)

    dst = cv2.imread('/mnt/c/linuxmirror/art2.jpg') #background
    dst = cv2.resize(dst, dsize=None, fx=0.8, fy=0.8)
    test.rotate(60)
    test.show(dst, 1200, 100)
    happy.rotate(-90)
    happy.resize(0.2)
    happy.show(dst, 800, 200)
    kurage.resize(0.3)
    kurage.rotate(-5)
    kurage.show(dst, 500, 500)
    cv2.imwrite('/mnt/c/linuxmirror/animate2.jpg', dst)  
#    cv2.imshow('dst',dst)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()
