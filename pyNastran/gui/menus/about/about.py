"""The about menu credits 3rd party packages."""
import sys
import locale
import platform
from typing import Dict

import numpy
import scipy
import vtk
import pyNastran

from qtpy.QtCore import Qt
from qtpy import QtGui
from qtpy.QtWidgets import (
    QLabel, QPushButton, QGridLayout, QApplication, QHBoxLayout, QVBoxLayout,
    QTabWidget, QWidget, QScrollArea, QTextEdit, QMessageBox)

from pyNastran.gui import IS_LINUX, IS_MAC # IS_WINDOWS
from pyNastran.gui.qt_version import qt_name, PYQT_VERSION, is_pygments # qt_version,
from pyNastran.gui.utils.qt.pydialog import PyDialog

QT = """
  * PyQt5 Python bindings for Qt5, by Riverbank Computing Limited.

  * Scintilla, a source code editor widget, written by Neil Hodgson and many contributors.
""" if qt_name == 'PyQt5' else """
  * PySide2 Python bindings for Qt5, by Qt for Python.
"""

PYGMENTS = """
  * Pygments by Georg Brandl, Armin Ronacher, Tim Hatch, and contributors.
""" if is_pygments else ''

CREDITS = f"""
pyNastran was written by Steve Doyle since 2011.  This product contains the following third party modules:

  * Numpy array library, developed by many contributors.

  * Scipy scientific library, developed by many contributors.

  * Python, the programming language, written by Guido van Rossum and many contributors.

  * VTK Python bindings for Qt5, by Riverbank Computing Limited.

  * Qt5 cross-platform GUI toolkit, developed by many contributors.
{QT}
  * Python Imaging Library, developed by Secret Labs AB and Fredrik Lundh.
{PYGMENTS}
  * WingIDE, the primary IDE used for development, by Wingware.

I gratefully acknowledge the efforts of all that have contributed to these and the other open source products and tools that are used in the development of pyNastran.
""".replace('\n', '<br>')


class AboutWindow(PyDialog):
    """
    +-------------+
    | AboutWindow |
    +-------------+
    """
    def __init__(self, data, win_parent=None, show_tol=True):
        """
        Saves the data members from data and
        performs type checks
        """
        PyDialog.__init__(self, data, win_parent)

        self._default_font_size = data['font_size']

        self.setWindowTitle('About pyNastran GUI')
        self.create_widgets(show_tol)
        self.create_layout()
        self.set_connections()
        self.on_font(self._default_font_size)

    def create_widgets(self, show_tol):
        """creates the display window"""
        #-----------------------------------------------------------------------
        # closing
        self.update_button = QPushButton('Check for Updates')
        self.ok_button = QPushButton('OK')
        #self.cancel_button = QPushButton('Cancel')

    def create_layout(self):
        ok_cancel_box = QHBoxLayout()
        ok_cancel_box.addWidget(self.update_button)
        ok_cancel_box.addStretch()
        ok_cancel_box.addWidget(self.ok_button)
        #ok_cancel_box.addWidget(self.cancel_button)

        #---------------------
        version_tab, len_version = _version_tab(ok_cancel_box)
        package_tab = _package_tab(len_version)
        credits_tab = _credits_tab()
        # --------------------
        tab_widget = QTabWidget()
        tab_widget.addTab(version_tab, 'Version')
        tab_widget.addTab(package_tab, 'Packages')
        tab_widget.addTab(credits_tab, 'Credits')

        #---------------------
        vbox_outer = QVBoxLayout()
        vbox_outer.addWidget(tab_widget)
        vbox_outer.addLayout(ok_cancel_box)
        #---------------------

        self.setLayout(vbox_outer)
        #hint = vbox.sizeHint()
        #print(hint)

        # PySide2.QtCore.QSize(516, 212)
        #hint.setHeight(hint.height() * 1.3)
        #hint.setWidth(hint.width() * 1.1)
        #self.setFixedSize(hint)

    def set_connections(self):
        #"""creates the actions for the menu"""
        #self.method_pulldown.currentIndexChanged.connect(self.on_method)
        #self.zaxis_method_pulldown.currentIndexChanged.connect(self.on_zaxis_method)
        #self.plane_color_edit.clicked.connect(self.on_plane_color)

        #self.apply_button.clicked.connect(self.on_apply)
        self.update_button.clicked.connect(self.on_update)
        self.ok_button.clicked.connect(self.on_ok)
        #self.cancel_button.clicked.connect(self.on_cancel)

    def on_font(self, value=None):
        """update the font for the current window"""
        if value is None:
            value = self.font_size_edit.value()
        font = QtGui.QFont()
        font.setPointSize(value)
        self.setFont(font)

    def on_update(self):
        """check for a newer version"""
        if self.win_parent is None:
            return
        is_newer = self.win_parent._check_for_latest_version()
        if not is_newer:
            self.update_button.setDisabled(True)
            QMessageBox.about(self, 'About pyNastran GUI', 'PyNastran GUI is already up to date')

    def on_ok(self):
        """closes the window"""
        #passed = self.on_apply()
        #if passed:
        self.close()
        #self.destroy()

    #def on_cancel(self):
        #self.out_data['close'] = True
        #self.close()

def get_packages(len_version=80):
    """makes the packages data"""
    #if qt_version == 'pyqt5':
        #import PyQt5
        #qt_name = 'PyQt5'
        #_qt_version = PyQt5.__version__
    #elif qt_version == 'pyside2':
        #import PySide2
        #qt_name = 'PySide2'
        #_qt_version = PySide2.__version__
    #else:
        #raise NotImplementedError(qt_version)

    import importlib

    python = str(sys.version_info)

    'python_branch', 'python_revision', 'python_build', 'python_compiler', 'python_implementation',
    packages = {
        'Python' : python + ' ' * (len_version - len(python) + 10),
        'branch': platform.python_branch(),
        #'Python revision': platform.python_revision(),
        #'Python Build': str(platform.python_build()),
        'Compiler': platform.python_compiler(),
        'Implementation': platform.python_implementation(),
        'numpy' : numpy.__version__,
        'scipy' : scipy.__version__,
        #'matplotlib' : matplotlib.__version__,
        #'pandas' : pandas.__version__,
        'matplotlib' : 'N/A',
        'pandas' : 'N/A',
        'imageio' : 'N/A',
        'PIL' : 'N/A',
        'vtk' : vtk.VTK_VERSION,
        #'PyQt5':,
        qt_name : PYQT_VERSION,
    }
    for name in ['matplotlib', 'pandas', 'docopt', 'imageio', 'PIL']:
        try:
            module = importlib.import_module(name, package=None)
        except ImportError:
            continue
        packages[name] = module.__version__
    return packages

def get_version() -> Dict[str, str]:
    """makes the version data"""
    sys_platform = sys.platform
    localei, unused_encoding = locale.getdefaultlocale()
    try:
        os_version = str(sys.getwindowsversion())
    except:
        os_version = '???'

    pmsg = [
        'machine', 'platform', 'processor', 'architecture',
        # 'win32_ver',
        'system', 'version', # 'uname',
        'mac_ver', 'libc_ver',
    ]
    #if not IS_WINDOWS:
        #pmsg.remove('win32_ver')
    if not IS_LINUX:
        pmsg.remove('libc_ver')
    if not IS_MAC:
        pmsg.remove('mac_ver')


    cpu = platform.processor()
    #memory = str(sys.getsizeof(None))
    version_data = {
        'Product': 'pyNastran GUI',
        'Version': pyNastran.__version__,
        'Release Type': 'Final Release',
        'Release Date': pyNastran.__releaseDate__,
        #'Cache Directory': ,
        'OS' : f'win32 (sys.platform={sys_platform})',
        'OS Version' : os_version,
        'CPU': cpu,
        #'Bit': bit,
        #'Memory': memory,
        'Locale': localei,
    }
    for key in pmsg:
        value = getattr(platform, key)()
        version_data[key] = str(value)
    return version_data

def _version_tab(ok_cancel_box):
    """makes the version tab"""
    version_data = get_version()

    len_version = len(version_data['OS Version'])
    grid = grid_from_dict(version_data)

    hbox = QHBoxLayout()
    hbox.addLayout(grid)
    hbox.addStretch()

    vbox = QVBoxLayout()
    vbox.addLayout(hbox)
    vbox.addStretch()
    #vbox.addLayout(ok_cancel_box)

    #---------------------
    version_tab = QWidget()
    version_tab.setLayout(vbox)

    return version_tab, len_version

def _package_tab(len_version=80):
    """makes the packages tab"""
    packages = get_packages(len_version=len_version)
    grid = grid_from_dict(packages)

    vbox = QVBoxLayout()
    vbox.addLayout(grid)
    vbox.addStretch()

    package_tab = QWidget()
    package_tab.setLayout(vbox)
    return package_tab

def grid_from_dict(mydict):
    irow = 0
    grid = QGridLayout()
    for key, valuei in mydict.items():
        label = QLabel(key + ':')
        label.setAlignment(Qt.AlignRight)

        value = QLabel(valuei)
        value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        grid.addWidget(label, irow, 0)
        grid.addWidget(value, irow, 1)
        irow += 1
    return grid

def _credits_tab():
    """creates the credits tab"""
    scroll_area = QScrollArea()
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scroll_area.setWidgetResizable(True)
    scroll_widget = QWidget(scroll_area)

    package_tab = QWidget()
    scroll_area.setWidget(package_tab)

    vbox = QVBoxLayout(scroll_widget)
    text = QTextEdit(CREDITS)
    text.setReadOnly(True)
    vbox.addWidget(text)

    package_tab = QWidget()
    package_tab.setLayout(vbox)
    return package_tab

def main():  # pragma: no cover
    # kills the program when you hit Cntl+C from the command line
    # doesn't save the current state as presumably there's been an error
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)


    import sys
    # Someone is launching this directly
    # Create the QApplication
    app = QApplication(sys.argv)
    #The Main window
    data = {
        'font_size' : 8,
    }
    main_window = AboutWindow(data, show_tol=True)
    main_window.show()
    # Enter the main loop
    app.exec_()

if __name__ == "__main__":
    main()