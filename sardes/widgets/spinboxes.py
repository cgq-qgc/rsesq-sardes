# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © SARDES Project Contributors
# https://github.com/cgq-qgc/sardes
#
# This file is part of SARDES.
# Licensed under the terms of the GNU General Public License.
# -----------------------------------------------------------------------------

# ---- Third party imports
from qtpy.QtCore import QSize, Signal
from qtpy.QtWidgets import QWidget, QHBoxLayout, QDoubleSpinBox, QLabel

# ---- Local imports
from sardes.config.icons import get_icon
from sardes.utils.qthelpers import format_tooltip


class IconSpinBox(QWidget):
    """
    A spinbox with an icon to its left.
    """
    sig_value_changed = Signal(float)

    def __init__(self, icon, value=0, value_range=(0, 99), decimals=0,
                 single_step=1, suffix=None, text=None, tip=None, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(1)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setDecimals(decimals)
        self.spinbox.setRange(*value_range)
        self.spinbox.setSingleStep(single_step)
        self.spinbox.setValue(value)
        self.spinbox.valueChanged.connect(self.sig_value_changed.emit)
        if suffix is not None:
            self.spinbox.setSuffix(suffix)

        icon_label = QLabel()
        icon_label.setPixmap(get_icon(icon).pixmap(
            QSize(self.spinbox.sizeHint().height(),
                  self.spinbox.sizeHint().height())))

        layout.addWidget(icon_label)
        layout.addWidget(self.spinbox)

        if any((text, tip)):
            self.spinbox.setToolTip(format_tooltip(text, tip, None))
            icon_label.setToolTip(format_tooltip(text, tip, None))

    # ---- QHBoxLayout public API
    def setContentsMargins(self, *margins):
        return self.layout().setContentsMargins(*margins)

    # ---- QDoubleSpinBox public API
    def setValue(self, val):
        return self.spinbox.setValue(val)

    def value(self):
        return self.spinbox.value()


class SpecialSpinBox(QDoubleSpinBox):
    """
    A spinbox that displays a special_text string whenever the current value
    is equal to a special_value.
    For example, if the special_text is set to 'max' and the special_val is set
    to 10.3, the spinbox will display 'max' instead of '10.3' whenever the
    current value of the spinbox equals to 10.3. Moreover, if the user enters
    the value 'text' in the spinbox, the current value will be silently set to
    10.3 and the spinbox will display the value 'text' instead of '10.3'.
    """
    sig_value_changed = Signal(object)
    def __init__(self, special_text: str, special_val: float = None,
                 title: str = None, desc: str = None):
        self._special_text = special_text
        self._special_text_intermediate = []
        for i in range(1, len(special_text)):
            self._special_text_intermediate.extend(
                ''.join(c) for c in itertools.combinations('max', i)
                )
        self._special_val = None
        self._special_on = False
        self._title = title
        self._desc = desc
        super().__init__()
        self.setKeyboardTracking(False)
        self.setMinimum(0.1)
        self.setMaximum(999.9)
        self.setSingleStep(1)
        self.setDecimals(1)
        self.setValue(20)
        self.valueChanged.connect(
            lambda: self.sig_value_changed.emit(self.value()))
        self.editingFinished.connect(
            lambda: self.sig_value_changed.emit(self.value()))
        if special_val is not None:
            self.set_special_value(special_val)
    def event(self, e):
        """
        Extend Qt method to update the tooltip.
        """
        if e.type() == QEvent.ToolTip:
            ttip = ''
            if self._title is not None:
                ttip += self._title
            ttip += "<p>Value: {val:0.{prec}f}</p>".format(
                val=super().value(), prec=self.decimals())
            if self._desc is not None:
                ttip += self._desc
            self.setToolTip(ttip)
        return super().event(e)
    def set_special_value(self, val):
        self._special_val = round(val, self.decimals())
        if self._special_on is True:
            super().setValue(self._special_val)
    def value(self):
        if self._special_on is True:
            return None
        else:
            return super().value()
    def sizeHint(self):
        qsize = super().sizeHint()
        qsize.setWidth(qsize.width() + 8)
        return qsize

    def validate(self, _input, pos):
        if _input in self._special_text_intermediate:
            return QValidator.Intermediate, _input, pos
        elif _input == 'max':
            return QValidator.Acceptable, _input, pos
        else:
            return super().validate(_input, pos)

    def valueFromText(self, text):
        if text == self._special_text:
            self._special_on = True
            super().setValue(self._special_val)
            return self._special_val
        else:
            return super().valueFromText(text)
    def textFromValue(self, val):
        val = round(val, self.decimals())
        if val == self._special_val and self._special_on:
            return self._special_text
        else:
            self._special_on = False
            return str(val)