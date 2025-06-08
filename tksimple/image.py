import os
import tkinter as _tk

from .const import TKExceptions
from .tkmath import Location2D, Rect



class PILImage:
    """
    Pillow image adapter for tkinter.
    Use 'PILImage.loadImage(<path>)' to load image from string path.
    Or use 'PILImage.loadImageFromPIL(<path>)' to load image from PIL.Image object.
    Used for advanced image progression.
    Package 'PIL.Image' have to be installed.
    """
    def __init__(self, image):
        import PIL.Image as Image
        self.copy = self.clone # redundant method
        self._preRenderedImage = None
        self._pilImage = Image # save pil.image from import!
        self._useOrg = False
        if isinstance(image, str):
            self._image = self._pilImage.open(image)
        elif isinstance(image, Image.Image):
            self._image = image
        else:
            raise TKExceptions.InvalidUsageException("Use 'Image.loadImage(<path>)' instead! Not:"+str(type(image)))
        self._original = self._image.copy()
    def __del__(self):
        self._original.close()
        self._image.close()
        del self._pilImage
    @staticmethod
    def loadImage(path:str):
        if os.path.exists(path):
            return PILImage(path)
        else:
            raise TKExceptions.PathNotExisits("This path does not Exists: "+str(path))
    @staticmethod
    def loadImageFromPIL(image):
        return PILImage(image)
    def clone(self, useOriginal=False):
        """
        Copies the image and returns a new image instance.
        @param useOriginal: if the original image should be taken.
        @return:
        """
        return PILImage(self._image.copy() if not useOriginal else self._original.copy())
    def toOriginal(self):
        """
        Resets the Image to original.
        @return:
        """
        self._image = self._original.copy()
        return self
    def resizeToIcon(self, useOriginal=False):
        """
        Resizes the image to default 16x16 icon size.
        @param useOriginal: if the original image should be taken.
        @return:
        """
        #256x256
        if useOriginal:
            self._image = self._original.resize((16, 16))
        else:
            self._image = self._image.resize((16, 16))
        return self
    def resize(self, fac:float, useOriginal=False):
        """
        Resizes the image with given factor.
        @param fac: factor for resize
        @param useOriginal: if the original image should be taken.
        @return:
        """
        if useOriginal:
            self._image = self._original.resize((int(round(self._original.width * fac, 0)), int(round(self._original.height * fac, 0))))
        else:
            self._image = self._image.resize((int(round(self._image.width * fac, 0)), int(round(self._image.height * fac, 0))))
        return self
    def resizeTo(self, x, y=None, useOriginal=False):
        """
        Resizes the image to fix size.
        @param x: int or Location2D instance
        @param y: int or None
        @param useOriginal: if the original image should be taken.
        @return:
        """
        if isinstance(x, Rect):
            x, y = x.getWidth(), x.getHeight()
        x = int(round(x, 0))
        y = int(round(y, 0))
        if useOriginal:
            self._image = self._original.resize((x, y))
        else:
            self._image = self._image.resize((x, y))
        return self
    def crop(self, loc:Location2D, loc2:Location2D, useOriginal=False):
        """
        Crops a square out of the image.
        @param loc: Location2D instance representing the first location
        @param loc2: Location2D instance representing the second location
        @param useOriginal: if the original image should be taken.
        @return:
        """
        if useOriginal:
            self._image = self._original.crop((*loc.get(), *loc2.get()))
        else:
            self._image = self._image.crop((*loc.get(), *loc2.get()))
        return self
    def getWidth(self):
        """
        Returns the current width of the image.
        @return:
        """
        return self._image.width
    def getHeight(self):
        """
        Returns the current width of the image.
        @return:
        """
        return self._image.height
    def preRender(self):
        """
        Converts the image to tkinter image.
        Call this earlyer in your code if an image error occurs.
        @return:
        """
        import PIL.ImageTk as imgTk
        self._preRenderedImage = imgTk.PhotoImage(self._image)
        return self
    def rotate(self, ang:int, useOriginal=False):
        if useOriginal:
            self._image = self._original.rotate(ang)
        else:
            self._image = self._image.rotate(ang)
        return self
    def _get(self):
        if self._preRenderedImage is None:
            self.preRender()
            img = self._preRenderedImage
            self._preRenderedImage = None
            return img
        else:
            return self._preRenderedImage
    def _getPIL(self):
        return self._image
class TkImage:
    """
    Default tkinter image adapter.
    Use 'TkImage.loadImage(<path>)' to load image from string path.
    """
    def __init__(self, image:_tk.PhotoImage):
        if isinstance(image, _tk.PhotoImage):
            self.image = image
        else:
            raise TKExceptions.InvalidUsageException("Use 'Image.loadImage(<path>)' instad! Not:" + str(type(image)))
    @staticmethod
    def loadImage(path:str):
        if os.path.exists(path):
            return TkImage(_tk.PhotoImage(file=path))
        else:
            raise TKExceptions.PathNotExisits("This path does not Exists: " + str(path))
    def resize(self, f:int):
        """
        Resizes the image using the tkinter 'subsample' method.
        @param f:
        @return:
        """
        self.image = self.image.subsample(f)
    def getWidth(self):
        """
        Returns the current width of the image.
        @return:
        """
        return int(self.image["width"])
    def getHeight(self):
        """
        Returns the current width of the image.
        @return:
        """
        return int(self.image["height"])
    def _get(self):
        return self.image