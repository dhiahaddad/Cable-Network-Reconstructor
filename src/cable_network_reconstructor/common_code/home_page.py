from PySide6 import QtCore
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .common_qt_widgets import HeaderWidget, PushButton
from .YamlLoader import YamlLoader


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = YamlLoader.get_reconstruction_config()
        self.initUI()

    def initUI(self):
        # Set up the layout
        layout = QVBoxLayout()

        header = HeaderWidget("")
        layout.addWidget(header)

        # Title
        title_font_size = int(self.height() * 0.15)
        title = QLabel("Cable Diagnosis Prototype")
        title.setStyleSheet(
            f"font-size: {title_font_size}px; font-weight: bold; text-align: center;"
        )
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        request_font_size = int(title_font_size / 2)
        request = QLabel("Select the type of test you want to run")
        request.setStyleSheet(
            f"font-size: {request_font_size}px; font-weight: normal; text-align: center;"
        )
        request.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(request)

        # Buttons
        element_height = self.height() * 0.15
        fault_location_layout = QHBoxLayout()

        self.reconstrBtn = PushButton(
            "Fault Location in Unknown Topology", element_height
        )

        # Add buttons to layout
        layout.addLayout(fault_location_layout)
        layout.addWidget(self.reconstrBtn)

        # Set layout to the widget
        self.setLayout(layout)
