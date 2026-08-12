import pickle
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QCheckBox,
)
from PySide6.QtGui import QPixmap, QFont
from PySide6 import QtCore, QtGui
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class InputField_QSpinBox(QWidget):
    def __init__(self, label: str, parent=None):
        super(InputField_QSpinBox, self).__init__(parent)
        self.initUI(label)

    def initUI(self, label):
        layout = QHBoxLayout()

        element_height = int(self.height() * 0.1)

        # Set font size
        font_size = int(element_height * 0.3)
        font = QFont("Sanserif")
        font.setPointSize(font_size)

        self.input_field = QSpinBox()
        self.input_field.setFixedHeight(element_height)
        self.input_field.setFont(font)
        self.input_field.setMaximum(500)

        self.label = QLabel(label + ":")
        self.label.setFont(font)

        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        self.setLayout(layout)

    def setValue(self, value):
        self.input_field.setValue(value)


class InputField_QDoubleSpinBox(QWidget):
    def __init__(self, label: str, parent=None):
        super(InputField_QDoubleSpinBox, self).__init__(parent)
        self.initUI(label)

    def initUI(self, label):
        layout = QHBoxLayout()

        element_height = int(self.height() * 0.1)

        # Set font size
        font_size = int(element_height * 0.3)
        font = QFont("Sanserif")
        font.setPointSize(font_size)

        self.input_field = QDoubleSpinBox()
        self.input_field.setFixedHeight(element_height)
        self.input_field.setFont(font)

        self.label = QLabel(label + ":")
        self.label.setFont(font)

        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        self.setLayout(layout)

    def setValue(self, value):
        self.input_field.setValue(value)


class InputFileSelector(QWidget):
    file_path: str

    def __init__(self, label: str, file_path: str, parent=None):
        super(InputFileSelector, self).__init__(parent)
        self.file_path = file_path
        self.label_txt = label
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        element_height = self.height() * 0.1
        self.input_file_btn = PushButton("Select File", element_height)
        self.run_analysis_btn = PushButton("Run Analysis", element_height)
        model_name = self.file_path.split("/")[-1]
        self.label = QLabel(self.label_txt + ": " + model_name)
        self.label.setWordWrap(True)  # Enable word wrapping
        # Set font size
        font_size = int(element_height * 0.3)
        font = QFont()
        font.setPointSize(font_size)
        self.label.setFont(font)

        self.input_file_btn.clicked.connect(self.select_input_file)
        layout.addWidget(self.label)
        layout.addWidget(self.input_file_btn)
        layout.addWidget(self.run_analysis_btn)
        self.setLayout(layout)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", self.file_path, "All Files (*)"
        )
        if file_path:
            self.file_path = file_path
            model_name = file_path.split("/")[-1]
            self.label.setText(self.label_txt + ": " + model_name)


class ImageWidget(QGroupBox):
    def __init__(self, title, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.initUI()
        self.setTitle(title)

    def initUI(self):
        font_size = int(self.height() * 0.03)
        self.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        self.network_image = QLabel()
        self.network_image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.network_image.setPixmap(QPixmap())  # Placeholder for the image
        layout.addWidget(self.network_image)
        self.setLayout(layout)

    def set_image(self, image_path):
        self.network_image.setPixmap(QPixmap(image_path))


class MatplotlibWidget(QGroupBox):
    def __init__(self, title, path, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.path = path
        self.canvas = FigureCanvas()
        self.initUI()
        self.setTitle(title)

    def initUI(self):
        font_size = int(self.height() * 0.03)
        self.setFont(QtGui.QFont("Sanserif", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout = QHBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self):
        with open(self.path, "rb") as file:
            figure = pickle.load(file)
            self.canvas.figure = figure
        self.canvas.draw()


class OutputField(QHBoxLayout):
    def __init__(self, label: str, value: str, parent: QWidget | None = None) -> None:
        if parent is None:
            super(OutputField, self).__init__()
        else:
            super(OutputField, self).__init__(parent)
        self.initUI(label, value)

    def initUI(self, label, value):
        self.label = QLabel(label)
        self.value = QLabel(value)
        font_size = int(self.label.height() * 0.03)
        self.label.setFont(QtGui.QFont("Courier", font_size))
        self.value.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.addWidget(self.label)
        self.addWidget(self.value)


class PushButton(QPushButton):
    def __init__(self, label: str, height, parent=None):
        super(PushButton, self).__init__(label, parent)
        self.initUI(height)

    def initUI(self, height):

        # Set button size
        self.setFixedHeight(int(height))

        # Set font size
        font_size = int(height * 0.3)
        font = QFont("Sanserif")
        font.setPointSize(font_size)
        self.setFont(font)


class OutputText(QGroupBox):
    def __init__(self, title: str, height, parent=None):
        super(OutputText, self).__init__(parent)
        self._title = title
        self.initUI(height)

    def initUI(self, height):
        font_size = int(height / 10)
        self.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(int(height))

        layout = QHBoxLayout()
        self.text = QLabel()
        self.text.setFont(QtGui.QFont("Courier", font_size))
        layout.addWidget(self.text)
        self.setLayout(layout)

    def set_text(self, content: str):
        self.text.setText(self._title + ":\n" + content)


class HeaderWidget(QWidget):
    def __init__(self, title, parent=None):
        super(HeaderWidget, self).__init__(parent)
        self.initUI(title)

    def initUI(self, title):
        layout = QHBoxLayout()
        self.setLayout(layout)

        logo_tuc = QLabel()
        logo_tuc.setPixmap(QPixmap("logo_tuc.png"))
        logo_tuc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_tuc)

        logo_mst = QLabel()
        logo_mst.setPixmap(QPixmap("logo_mst.png"))
        logo_mst.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_mst)

        logo_latis = QLabel()
        logo_latis.setPixmap(QPixmap("logo_latis.png"))
        logo_latis.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_latis)

        logo_eniso = QLabel()
        logo_eniso.setPixmap(QPixmap("logo_eniso.png"))
        logo_eniso.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_eniso)


class PageTitleWidget(QGroupBox):
    def __init__(self, title, parent=None):
        super(PageTitleWidget, self).__init__(parent)
        self.initUI(title)

    def initUI(self, title):
        font_size = int(self.height() * 0.1)
        label = QLabel("Network Reconstructor")
        label.setFont(QtGui.QFont("Sanserif", font_size))
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setText(title)
        height = int(self.height() * 0.2)
        self.setMaximumHeight(height)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class FiguresGroup(QGroupBox):
    def __init__(self, title1, title2, path1, path2, parent=None):
        super(FiguresGroup, self).__init__(parent)
        self.initUI(title1, title2, path1, path2)

    def initUI(self, title1, title2, path1, path2):
        layout = QHBoxLayout()
        self.reflectogram = MatplotlibWidget(title1, path1)
        self.projection_graph = MatplotlibWidget(title2, path2)
        layout.addWidget(self.reflectogram)
        layout.addWidget(self.projection_graph)
        self.setLayout(layout)


class FaultLocatorInputs(QGroupBox):
    def __init__(self, parent=None):
        super(FaultLocatorInputs, self).__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        default_path0 = "input_files/bus_network/reference_topology.txt"
        default_path1 = "input_files/bus_network/R1.csv"
        default_path2 = "input_files/bus_network/R2.csv"
        self.input_file_selector0 = InputFileSelector(
            "Network topology description file", default_path0
        )
        layout.addWidget(self.input_file_selector0)
        self.input_file_selector1 = InputFileSelector("R1 input file", default_path1)
        layout.addWidget(self.input_file_selector1)
        self.input_file_selector2 = InputFileSelector("R2 input file", default_path2)
        layout.addWidget(self.input_file_selector2)

        self.start_btn = PushButton("Locate Faults", self.height() * 0.1)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)


class CheckBox(QWidget):
    def __init__(self, label: str, parent=None):
        super(CheckBox, self).__init__(parent)
        self.initUI(label)

    def initUI(self, label: str):
        layout = QHBoxLayout()

        element_height = self.height() * 0.1

        self.label = QLabel(label)
        self.checkBox = QCheckBox()

        # Set the size of the checkbox using stylesheets
        self.checkBox.setStyleSheet(
            f"""
            QCheckBox::indicator {{
                width: {element_height}px;
                height: {element_height}px;
            }}
        """
        )

        self.checkBox.setChecked(False)
        font_size = int(self.label.height() * 0.03)
        self.label.setFont(QtGui.QFont("Sanserif", font_size))

        layout.addWidget(self.label)
        layout.addWidget(self.checkBox)

        layout.addWidget(self.label)
        layout.addWidget(self.checkBox)
        self.setLayout(layout)

    def isChecked(self):
        return self.checkBox.isChecked()

    def setChecked(self, value: bool):
        self.checkBox.setChecked(value)
