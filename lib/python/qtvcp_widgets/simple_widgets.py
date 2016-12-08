import gobject
from PyQt4 import QtCore,QtGui
from functools import partial
import hal

hal_pin_changed_signal = ('hal-pin-changed', (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_OBJECT,)))

""" Set of base classes """
class _HalWidgetBase:
    def hal_init(self, comp, name, object):
        self.hal, self.hal_name = comp, name
        self.qt_object = object
        self._hal_init()

    def _hal_init(self):
        """ Child HAL initialization functions """
        pass

    def hal_update(self):
        """ Update HAL state """
        pass

class _HalToggleBase(_HalWidgetBase):
    def _hal_init(self):
        self.hal_pin = self.hal.newpin(self.hal_name, hal.HAL_BIT, hal.HAL_OUT)
        self.hal_pin_not = self.hal.newpin(self.hal_name + "-not", hal.HAL_BIT, hal.HAL_OUT)
        QtCore.QObject.connect(self.qt_object, QtCore.SIGNAL("stateChanged(int)"), partial(self.t_update))

    def t_update(self,state):
        sender = self.sender()
        self.hal_pin.set(bool(state))
        self.hal_pin_not.set(not bool(state))

class _HalScaleBase(_HalWidgetBase):
    def _hal_init(self):
        self.hal_pin = self.hal.newpin(self.hal_name, hal.HAL_FLOAT, hal.HAL_OUT)
        #self.connect("value-changed", self.hal_update)

    def hal_update(self, *a):
        pass
        self.hal_pin.set(self.get_value())

######################
# REAL WIDGETS
######################

class Lcnc_LCDNumber(QtGui.QLCDNumber, _HalWidgetBase):
    def __init__(self, parent = None):
        QtGui.QLCDNumber.__init__(self, parent)
    def _hal_init(self):
        self.hal_pin = self.hal.newpin(self.hal_name, hal.HAL_FLOAT, hal.HAL_IN)
        self.hal_pin.connect('value-changed',lambda p: self.l_update(p))
    def l_update(self,d):
        self.display(d.get())

class Lcnc_CheckBox(QtGui.QCheckBox, _HalToggleBase):
    def __init__(self, parent = None):
        QtGui.QCheckBox.__init__(self, parent)

class Lcnc_PushButton(QtGui.QPushButton, _HalWidgetBase):
    def __init__(self, parent = None):
        QtGui.QPushButton.__init__(self, parent)
    def _hal_init(self):
        self.hal_pin = self.hal.newpin(str(self.hal_name), hal.HAL_BIT, hal.HAL_OUT)
        def _f(data):
                self.hal_pin.set(data)
        QtCore.QObject.connect(self.qt_object, QtCore.SIGNAL("pressed()"), partial(_f,True))
        QtCore.QObject.connect(self.qt_object, QtCore.SIGNAL("released()"), partial(_f,False))

