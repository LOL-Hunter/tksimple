import tkinter.colorchooser as _clc
import tkinter.filedialog as _fd
import tkinter.messagebox as _msgb
import tkinter.simpledialog as _simd
import os
from time import sleep

from .window import Tk, Dialog
from .widget import Listbox, Button, Label, Entry
from .const import TKExceptions, EventType

class FileDialog:
    @staticmethod
    def openFile(master=None, title=None, initialpath=None, types=None):
        if types is None:
            types = []
        return FileDialog._dialog(_fd.askopenfilename, master=master, title=title, initialpath=initialpath, types=types)
    @staticmethod
    def openDirectory(master=None, title=None, initialpath=None):
        return FileDialog._dialog(_fd.askdirectory, master=master, title=title, initialpath=initialpath)
    @staticmethod
    def saveFile(master=None, title=None, initialpath=None, types:list=None):
        if types is None:
            types = []
        return FileDialog._dialog(_fd.asksaveasfilename, master=master, title=title, initialpath=initialpath, types=types)
    @staticmethod
    def _dialog(func, master=None, title=None, initialpath=None, types=None):
        if types is None:
            types = []
        destroy=False
        _types = (("", "",), ("", "",))
        if type(types) == list:
            for i in types:
                if str(i).startswith("."):
                    _types += (("", "*"+str(i),),)
                elif str(i).startswith("*."):
                    _types += (("", str(i),),)
                else:
                    raise TKExceptions.InvalidFileExtention(str(i)+" is not a valid Extention! Use .<ext>!")
        _data = {"title":str(title),
                "initialdir":initialpath}
        if func != _fd.askdirectory: _data["filetypes"] = _types
        if initialpath is not None and os.path.split(initialpath)[1]!="" and False:# Disabled
            _data["initialfile"] = os.path.split(initialpath)[1]
        if master is None:
            destroy = True
            master = Tk()
            master.hide()
            _data["parent"] = master._get()
class SimpleDialog:
    @staticmethod
    def askYesNo(master, message="", title=""):
        return SimpleDialog._dialog(_msgb.askyesno, master, message=message, title=title)
    @staticmethod
    def askYesNoCancel(master, message="", title=""):
        """
        yes    -> True
        no     -> False
        cancel -> None
        @param master:
        @param message:
        @param title:
        @return:
        """
        return SimpleDialog._dialog(_msgb.askyesnocancel, master, message=message, title=title)
    @staticmethod
    def askOkayCancel(master, message="", title=""):
        """

        @rtype: object
        @param master:
        @param message:
        @param title:
        @return: True or False
        """
        return SimpleDialog._dialog(_msgb.askokcancel, master, message=message, title=title)
    @staticmethod
    def askRetryCancel(master, message="", title=""):
        return SimpleDialog._dialog(_msgb.askretrycancel, master, message=message, title=title)
    @staticmethod
    def askInfo(master, message="", title=""):
        return SimpleDialog._dialog(_msgb.showinfo, master, message=message, title=title)
    @staticmethod
    def askError(master, message="", title=""):
        return SimpleDialog._dialog(_msgb.showerror, master, message=message, title=title)
    @staticmethod
    def askWarning(master, message="", title=""):
        return SimpleDialog._dialog(_msgb.showwarning, master, message=message, title=title)
    @staticmethod
    def askString(master, message="", title="", initialValue="", hideWith=None)-> str | None:
        return SimpleDialog._dialog(_simd.askstring, master, prompt=message, title=title, show=hideWith, initialvalue=initialValue)
    @staticmethod
    def askInteger(master, message="", title="", initialValue=""):
        return SimpleDialog._dialog(_simd.askinteger, master, prompt=message, title=title)
    @staticmethod
    def askFloat(master, message="", title="", initialValue=""):
        return SimpleDialog._dialog(_simd.askfloat, master, prompt=message, title=title)
    @staticmethod
    def askUsernamePassword(master, title="", initialUname="", initialPassw="", unameString="Username:", passwString="Password:", hidePassword=True, default=None, group=None):
        _return = None
        _masterNone = False

        def cancel(e):
            nonlocal _return
            _return = "None"
        def select(e):
            nonlocal _return
            un = unE.getValue()
            pw = pwE.getValue()
            _return = [un, pw]

        def onClose():
            nonlocal _return
            _return = "None"

        if master is None:
            _masterNone = True
            master = Tk()
            master.hide()
        dialog = Dialog(master, group=group)
        dialog.setTitle(title)
        dialog.setResizeable(False)
        dialog.setWindowSize(200, 125)
        dialog.onCloseEvent(onClose)
        dialog.bind(select, EventType.RETURN)
        dialog.bind(cancel, EventType.ESC)

        unL = Label(dialog, group=group).placeRelative(fixY=0, fixHeight=25, centerX=True, fixWidth=100).setText(unameString)
        unE = Entry(dialog, group=group).placeRelative(fixY=25, fixHeight=25, centerX=True, fixWidth=100).setValue(initialUname)
        pwL = Label(dialog, group=group).placeRelative(fixY=50, fixHeight=25, centerX=True, fixWidth=100).setText(passwString)
        pwE = Entry(dialog, group=group).placeRelative(fixY=75, fixHeight=25, centerX=True, fixWidth=100).setValue(initialPassw)
        if hidePassword: pwE.hideCharactersWith("*")

        cancB = Button(dialog, group=group).setCommand(cancel).placeRelative(fixY=100, fixHeight=25, xOffsetLeft=50).setText("Cancel")
        okB = Button(dialog, group=group).setCommand(select).placeRelative(fixY=100, fixHeight=25, xOffsetRight=50).setText("OK")

        dialog.show()
        while True:
            master.update()
            sleep(.1)
            if _return == "None":
                if _masterNone: master.destroy()
                dialog.destroy()
                return None if default is None else default
            elif isinstance(_return, list):
                if _masterNone: master.destroy()
                dialog.destroy()
                return _return
    @staticmethod
    def chooseFromList(master, title="", values=None, chooseOnlyOne=True, forceToChoose=True, useIndexInstead=False, group=None)->str | int | list | None:
        _return = None
        _masterNone = False

        def cancel(e):
            nonlocal _return
            _return = "None"
        def select(e):
            nonlocal _return
            sel = list_.getSelectedIndex() if useIndexInstead else list_.getSelectedItem()
            if sel is None:
                if forceToChoose:
                    SimpleDialog.askError(dialog, "Please choose at least one!")
                else:
                    _return = "None"
            else:
                _return = [sel] if not isinstance(sel, list) else sel
        def onClose():
            nonlocal _return
            if not forceToChoose:
                _return = "None"

        if master is None:
            _masterNone = True
            master = Tk()
            master.hide()

        dialog = Dialog(master, group)
        dialog.onCloseEvent(onClose)
        if forceToChoose:
            dialog.setCloseable(False)
        dialog.setWindowSize(200, 200)
        dialog.setResizeable(False)
        dialog.setTitle(title)
        list_ = Listbox(dialog, group)
        if chooseOnlyOne:
            list_.setSingleSelect()
        else:
            list_.setMultipleSelect()
        list_.addAll(values)
        list_.placeRelative(changeHeight=-30)
        list_.bind(select, EventType.DOUBBLE_LEFT)

        Button(dialog, group).setText("Select").placeRelative(stickDown=True, fixHeight=30, xOffsetRight=50).setCommand(select)
        canc = Button(dialog, group).setText("Cancel").placeRelative(stickDown=True, stickRight=True, fixHeight=30, xOffsetRight=50).setCommand(cancel)
        if forceToChoose: canc.disable()
        dialog.show()
        while True:
            master.update()
            sleep(.1)
            if _return == "None":
                dialog.destroy()
                if _masterNone: master.destroy()
                return None
            elif isinstance(_return, list):
                dialog.destroy()
                if _masterNone: master.destroy()
                return _return[0] if chooseOnlyOne else _return
    @staticmethod
    def _dialog(d, master, **kwargs):
        if isinstance(master, Tk):
            if kwargs["title"] == "":
                kwargs["title"] = master["title"]
            return d(parent=master._get(), **kwargs)
        else:
            mas = Tk()
            mas.hide()
            anw = d(parent=mas._get(), **kwargs)
            mas.destroy()
            return anw
class ColorChooser:
    def __init__(self, c):
        self._c = c
    def getCanceled(self):
        return self._c == (None, None)
    def getHex(self):
        return self._c[1]
    def getRGB(self):
        return self._c[0]
    def __str__(self):
        return self.getRGB()
    @staticmethod
    def askColor(master=None, initialcolor=None, title=""):
        if isinstance(master, Tk):
            if initialcolor == "": initialcolor = None
            return ColorChooser(_clc.askcolor(initialcolor=initialcolor.value if hasattr(initialcolor, "value") else initialcolor, parent=master._get(), title=str(title)))
        else:
            mas = Tk()
            mas.hide()
            anw = ColorChooser(_clc.askcolor(initialcolor=initialcolor.value if hasattr(initialcolor, "value") else master, parent=mas._get(), title=title))
            mas.destroy()
            return anw
