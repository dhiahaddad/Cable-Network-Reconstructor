import logging

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from .common_code.common_qt_widgets import (
    CheckBox,
    ImageWidget,
    InputField_QDoubleSpinBox,
    InputField_QSpinBox,
    InputFileSelector,
    OutputField,
    PushButton,
)
from .common_code.YamlLoader import YamlLoader
from .data.data_classes import Statistics, TestCase
from .signal_processor import SignalProcessorFactory


class FiguresLayout(QHBoxLayout):
    def __init__(self, parent=None):
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.original_network = ImageWidget("Original Network")
        self.reconstructed_network = ImageWidget("Reconstructed Network")
        self.addWidget(self.original_network)
        self.addWidget(self.reconstructed_network)

    def update_figures(self, original_image_path, reconstructed_image_path):
        self.original_network.set_image(original_image_path)
        self.reconstructed_network.set_image(reconstructed_image_path)


class Legend(QHBoxLayout):
    def __init__(self, parent=None):
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)
        self.initUI()

    def initUI(self):
        legend = ImageWidget("Legend")
        legend.set_image("Nodes Legend.png")

        self.addWidget(legend)


class SingleTest(QVBoxLayout):
    def __init__(self, parent=None):
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.test_result_group = TestCaseResults()
        self.addWidget(self.test_result_group)
        legend = Legend()
        self.addLayout(legend)
        self.figures_layout = FiguresLayout()
        self.addLayout(self.figures_layout)

    def update_figures(self, parent_folder: str, model_name: str) -> None:
        original_image_path = (
            f"{parent_folder}/../../../reconstructed_networks/{model_name}_reference"
        )
        reconstructed_image_path = f"{parent_folder}/../../../reconstructed_networks/{model_name}_reconstructed"
        self.figures_layout.update_figures(
            original_image_path, reconstructed_image_path
        )

    def update_test_case_results(self, test_case: TestCase):
        self.test_result_group.update_results(test_case)


class MultiTest(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setTitle("Multiple Test Results")

    def initUI(self):
        font_size = int(self.height() * 0.03)
        self.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()

        self.number_of_tests = OutputField("Number of tests:\t\t\t", "-")
        self.number_of_successful_tests = OutputField(
            "Number of successful tests:\t\t", "-"
        )
        self.success_output = OutputField("Success percentage:\t\t", "-")
        self.average_time = OutputField("Average processing time per test:\t", "-")
        self.time_output = OutputField("Total processing time:\t\t", "-")
        layout.addLayout(self.number_of_tests)
        layout.addLayout(self.number_of_successful_tests)
        layout.addLayout(self.success_output)
        layout.addLayout(self.average_time)
        layout.addLayout(self.time_output)

        self.dropdown_menu = QComboBox()
        self.dropdown_menu.addItem("Option 1")
        self.dropdown_menu.addItem("Option 2")
        self.dropdown_menu.addItem("Option 3")
        self.dropdown_menu.setFont(QtGui.QFont("Courier", font_size))
        layout.addWidget(self.dropdown_menu)

        self.setLayout(layout)

    def update_statistics(self, statistics: Statistics):
        self.success_output.value.setText(str(statistics.success_percentage) + "%")
        self.time_output.value.setText(
            f"{statistics.processing_time:,.0f}".replace(",", "'") + " microseconds"
        )
        self.number_of_tests.value.setText(
            str(statistics.total_tests_number) + " tests"
        )
        self.number_of_successful_tests.value.setText(
            str(statistics.successful_tests_number) + " tests"
        )
        self.average_time.value.setText(
            f"{statistics.processing_time / statistics.total_tests_number:,.0f}".replace(
                ",", "'"
            )
            + " microseconds"
        )


class SingleTestInputs(QGroupBox):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.initUI()
        self.setTitle("Input Parameters")

    def initUI(self):
        font_size = int(self.height() * 0.03)
        self.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()

        file_name = YamlLoader.get_safe(
            self.config, "reconstruction_conf.file_name", ""
        )
        self.input_file_selector = InputFileSelector("Input file", file_name)
        layout.addWidget(self.input_file_selector)

        self.excitation_type = QComboBox()
        self.excitation_type.addItem("Step")
        self.excitation_type.addItem("Impulse")
        excitation_type = YamlLoader.get_safe(
            self.config, "reconstruction_conf.excitation_type", "Step"
        )
        self.excitation_type.setCurrentText(excitation_type)
        self.excitation_type.setFont(QtGui.QFont("Courier", font_size))
        layout.addWidget(self.excitation_type)

        self.detect_soft_faults = CheckBox("Detect Soft Faults          ")
        detect_soft_faults = YamlLoader.get_safe(
            self.config, "reconstruction_conf.detect_soft_faults", False
        )
        self.detect_soft_faults.setChecked(detect_soft_faults)
        layout.addWidget(self.detect_soft_faults)

        self.path_length_input = InputField_QSpinBox("Path Length")
        path_length = YamlLoader.get_safe(
            self.config, "reconstruction_conf.path_length", 15
        )
        self.path_length_input.setValue(int(path_length))
        layout.addWidget(self.path_length_input)

        self.peak_threshold_input = InputField_QDoubleSpinBox("Peak Threshold")
        peak_height = YamlLoader.get_safe(
            self.config, "reconstruction_conf.peak_height", 0.01
        )
        self.peak_threshold_input.setValue(float(peak_height))
        layout.addWidget(self.peak_threshold_input)

        run_test_buttons_layout = QHBoxLayout()

        element_height = self.height() * 0.1
        self.single_test_btn = PushButton("Run Test", element_height)
        self.nxt_lvl_btn = PushButton("Run Next Level Test", element_height)
        run_test_buttons_layout.addWidget(self.single_test_btn)
        run_test_buttons_layout.addWidget(self.nxt_lvl_btn)
        layout.addLayout(run_test_buttons_layout)
        self.setLayout(layout)


class MultiTestInputs(QGroupBox):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.initUI()
        self.setTitle("Multiple Cable Network Reconstruction")

    def initUI(self):
        font_size = int(self.height() * 0.03)
        self.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()

        self.num_files_input = InputField_QSpinBox("Number of Files")
        tests_number = YamlLoader.get_safe(
            self.config, "reconstruction_conf.tests_number", 50
        )
        self.num_files_input.setValue(tests_number)
        layout.addWidget(self.num_files_input)

        self.min_complexity_input = InputField_QSpinBox("Min Network Complexity")
        min_complexity = YamlLoader.get_safe(
            self.config, "reconstruction_conf.min_complexity", 2
        )
        self.min_complexity_input.setValue(min_complexity)
        layout.addWidget(self.min_complexity_input)

        self.max_complexity_input = InputField_QSpinBox("Max Network Complexity")
        max_complexity = YamlLoader.get_safe(
            self.config, "reconstruction_conf.max_complexity", 6
        )
        self.max_complexity_input.setValue(max_complexity)
        layout.addWidget(self.max_complexity_input)

        element_height = self.height() * 0.1
        self.run_random_tests_btn = PushButton("Run Random Tests", element_height)
        layout.addWidget(self.run_random_tests_btn)

        self.setLayout(layout)


class TestCaseResults(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Test Results")
        self.initUI()

    def initUI(self):
        font_size = int(self.height() * 0.03)
        self.setFont(QtGui.QFont("Courier", font_size))
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        test_result_layout = QVBoxLayout()
        self.test_result_output = OutputField("Test result:", "-")
        self.test_time_output = OutputField("Processing time:", "-")
        # self.peaks_output = OutputField("Peaks:", "-")
        # self.unidentified_output = OutputField("Unidentified:", "-")
        # self.total_output = OutputField("Total:", "-")
        # self.level_output = OutputField("Level:", "-")
        test_result_layout.addLayout(self.test_result_output)
        test_result_layout.addLayout(self.test_time_output)
        # test_result_layout.addLayout(self.peaks_output)
        # test_result_layout.addLayout(self.unidentified_output)
        # test_result_layout.addLayout(self.total_output)
        # test_result_layout.addLayout(self.level_output)
        self.setLayout(test_result_layout)
        self.setLayout(test_result_layout)

    def update_results(self, test_case: TestCase):
        self.test_result_output.value.setText(
            "Correct" if test_case.test_result == "1" else "Incorrect"
        )
        self.test_time_output.value.setText(
            f"{test_case.processing_time:,.0f}".replace(",", "'") + " microseconds"
        )
        # self.peaks_output.value.setText(str(test_case.identified_peaks_number))
        # self.unidentified_output.value.setText(str(test_case.unidentified_peaks_number))
        # self.total_output.value.setText(str(test_case.peaks_number))
        # self.level_output.value.setText(str(test_case.reconstruction_level))


class DebouncedAnalyzer:
    def __init__(self, delay_ms, callback):
        self.timer = QTimer()
        self.timer.setInterval(delay_ms)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(callback)

    def trigger(self):
        self.timer.start()


class SliderWithLabel(QWidget):
    def __init__(
        self,
        label,
        min_val,
        max_val,
        n_steps,
        init_val,
        unit="",
        log=False,
        callback=None,
    ):
        super().__init__()
        self.callback = callback
        self.min_val = min_val
        self.max_val = max_val
        self.log = log
        self.n_steps = n_steps
        self.step = (max_val - min_val) / n_steps
        h = QHBoxLayout(self)
        h.addWidget(QLabel(label))
        self.edit = QLineEdit(f"{init_val:.4g}")
        self.edit.setFixedWidth(80)
        self.edit.editingFinished.connect(self._sync_from_edit)
        h.addWidget(self.edit)
        h.addWidget(QLabel(unit))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.n_steps)
        self.slider.setValue(self._val_to_slider(init_val))
        self.slider.valueChanged.connect(self._sync_from_slider)
        h.addWidget(self.slider)

    def _slider_to_val(self, s):
        return self.min_val + s * self.step

    def _val_to_slider(self, v):
        return int((v - self.min_val) / self.step)

    def _sync_from_slider(self, *a):
        v = self._slider_to_val(self.slider.value())
        self.edit.setText(f"{v:.4g}")
        if self.callback:
            self.callback()

    def _sync_from_edit(self):
        try:
            v = float(self.edit.text())
            v = max(self.min_val, min(self.max_val, v))
            self.slider.setValue(self._val_to_slider(v))
        except ValueError:
            pass

    def value(self):
        return float(self.edit.text())


class RangeSlider(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal):
        super().__init__()
        self.orientation = orientation
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(30)
        else:
            self.setFixedWidth(30)

        self._min = 0
        self._max = 100
        self._low = 0
        self._high = 100

        self._callbacks = []
        self._pressed_control = None
        self._last_emitted_values = None

    def setRange(self, min_val, max_val):
        self._min = min_val
        self._max = max_val
        self.update()

    def setValue(self, value_tuple):
        self._low, self._high = value_tuple
        self._low = max(self._min, min(self._max, self._low))
        self._high = max(self._min, min(self._max, self._high))
        if self._low > self._high:
            self._low, self._high = self._high, self._low
        self.update()

    def value(self):
        return (self._low, self._high)

    def valueChanged(self):
        class Signal:
            def __init__(self, parent):
                self.parent = parent

            def connect(self, callback):
                self.parent._callbacks.append(callback)

        return Signal(self)

    def _emit_value_changed(self):
        current_values = (self._low, self._high)
        if self._last_emitted_values != current_values:
            self._last_emitted_values = current_values
            for callback in self._callbacks:
                callback()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw track
        track_rect = self.rect().adjusted(10, 10, -10, -10)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.drawRect(track_rect)

        # Calculate positions
        range_size = self._max - self._min
        if range_size > 0:
            low_pos = (self._low - self._min) / range_size
            high_pos = (self._high - self._min) / range_size

            if self.orientation == Qt.Orientation.Horizontal:
                x1 = track_rect.left() + low_pos * track_rect.width()
                x2 = track_rect.left() + high_pos * track_rect.width()

                # Draw selected range
                painter.setBrush(QBrush(QColor(100, 150, 200)))
                painter.drawRect(
                    int(x1), track_rect.top(), int(x2 - x1), track_rect.height()
                )

                # Draw handles
                painter.setBrush(QBrush(QColor(50, 100, 150)))
                painter.drawEllipse(int(x1 - 5), track_rect.center().y() - 5, 10, 10)
                painter.drawEllipse(int(x2 - 5), track_rect.center().y() - 5, 10, 10)

    def mousePressEvent(self, event):
        track_rect = self.rect().adjusted(10, 10, -10, -10)
        range_size = self._max - self._min

        if range_size > 0 and self.orientation == Qt.Orientation.Horizontal:
            low_pos = (
                track_rect.left()
                + (self._low - self._min) / range_size * track_rect.width()
            )
            high_pos = (
                track_rect.left()
                + (self._high - self._min) / range_size * track_rect.width()
            )

            mouse_x = event.position().x()

            if abs(mouse_x - low_pos) < abs(mouse_x - high_pos):
                self._pressed_control = "low"
            else:
                self._pressed_control = "high"

    def mouseMoveEvent(self, event):
        if self._pressed_control and self.orientation == Qt.Orientation.Horizontal:
            track_rect = self.rect().adjusted(10, 10, -10, -10)
            mouse_x = event.position().x()

            relative_pos = (mouse_x - track_rect.left()) / track_rect.width()
            relative_pos = max(0, min(1, relative_pos))
            new_value = self._min + relative_pos * (self._max - self._min)

            old_low, old_high = self._low, self._high

            if self._pressed_control == "low":
                self._low = min(new_value, self._high)
            else:
                self._high = max(new_value, self._low)

            if old_low != self._low or old_high != self._high:
                self.update()
                self._emit_value_changed()

    def mouseReleaseEvent(self, event):
        self._pressed_control = None


class SignalProcessingWidget(QWidget):
    def __init__(self, config, parent_widget=None):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget  # TODO
        self.config = config or {}
        self.debouncer = DebouncedAnalyzer(100, self.analyze)
        self.signal_processor = None
        self._external_widgets = []  # List to store external widgets to manage
        self._init_ui()
        self._update_widget_states()  # Initialize widget states

    def add_external_widget(self, widget):
        """Add an external widget to be managed by the state system"""
        if widget is not None and widget not in self._external_widgets:
            self._external_widgets.append(widget)

    def remove_external_widget(self, widget):
        """Remove an external widget from state management"""
        if widget in self._external_widgets:
            self._external_widgets.remove(widget)

    def _is_network_loaded(self) -> bool:
        """Check if any data is currently loaded (S-parameter, CSV, or MAT)"""
        return self.signal_processor is not None

    def _get_processing_widgets(self) -> list:
        """Get list of widgets that should be disabled when no network is loaded"""
        widgets = [
            # Sliders for signal processing parameters
            self.dist_s,
            self.prom_s,
            self.speed_s,
            # Combo boxes for processing options
            self.win_cb,
            self.filter_cb,
            # Line edit for gating
            self.gate_le,
            # Checkboxes for plot options
            self.chk_freq,
            self.chk_time,
            # Range sliders for zoom
            self.freq_zoom,
            self.dist_zoom,
        ]

        # Add external widgets that have been registered
        widgets.extend(self._external_widgets)

        return widgets

    def _update_widget_states(self):
        """Update the enabled/disabled state of widgets based on network availability"""
        network_loaded = self._is_network_loaded()
        processing_widgets = self._get_processing_widgets()

        for widget in processing_widgets:
            if widget is not None:
                widget.setEnabled(network_loaded)

        # Update status message
        if hasattr(self, "status_label"):
            if network_loaded:
                self.status_label.setText(
                    "✅ Data loaded - processing parameters enabled"
                )
                self.status_label.setStyleSheet("color: green;")
            else:
                self.status_label.setText(
                    "⚠️ No data loaded - please select an input file first"
                )
                self.status_label.setStyleSheet("color: orange;")

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Parameters group
        params = QGroupBox("Signal Processing Parameters")
        form = QFormLayout()

        signal_config: dict = self.config.get("signal_processing_conf")

        h1 = QHBoxLayout()
        self.dist_s = SliderWithLabel(
            "Peak Dist (m):",
            0.001,
            1,
            10000,
            signal_config.get("peak_distance"),
            "m",
            callback=self.debouncer.trigger,
        )
        self.prom_s = SliderWithLabel(
            "Prominence:",
            0.001,
            0.01,
            10000,
            signal_config.get("prominence"),
            callback=self.debouncer.trigger,
        )
        self.speed_s = SliderWithLabel(
            "Speed (m/s):",
            1e7,
            3e8,
            10000,
            signal_config.get("speed"),
            "m/s",
            callback=self.debouncer.trigger,
        )
        h1.addWidget(self.dist_s)
        h1.addWidget(self.prom_s)
        h1.addWidget(self.speed_s)
        form.addRow(h1)

        h2 = QHBoxLayout()
        self.win_cb = QComboBox()
        self.win_cb.addItems(["hann", "hamming", "blackman", "boxcar"])
        self.win_cb.setCurrentText(signal_config.get("window"))
        self.win_cb.currentIndexChanged.connect(self.debouncer.trigger)
        self.filter_cb = QComboBox()
        self.filter_cb.addItems(["None", "Lowpass", "Highpass", "Bandpass"])
        self.filter_cb.setCurrentText(signal_config.get("filter"))
        self.filter_cb.currentIndexChanged.connect(self.debouncer.trigger)
        self.gate_le = QLineEdit(signal_config.get("gating"))
        self.gate_le.editingFinished.connect(self.debouncer.trigger)
        h2.addWidget(QLabel("Window:"))
        h2.addWidget(self.win_cb)
        h2.addWidget(QLabel("Filter:"))
        h2.addWidget(self.filter_cb)
        h2.addWidget(QLabel("Gating:"))
        h2.addWidget(self.gate_le)
        form.addRow(h2)

        h3 = QHBoxLayout()
        self.chk_freq = QCheckBox("Frequency Plot")
        self.chk_freq.setChecked(signal_config.get("show_frequency_plot", True))
        self.chk_freq.stateChanged.connect(self.debouncer.trigger)
        self.chk_time = QCheckBox("Distance Plot")
        self.chk_time.setChecked(signal_config.get("show_distance_plot", True))
        self.chk_time.stateChanged.connect(self.debouncer.trigger)
        self.chk_apply_derivative = QCheckBox("Apply Derivative")
        self.chk_apply_derivative.setChecked(
            signal_config.get("apply_derivative", False)
        )
        self.chk_apply_derivative.stateChanged.connect(self.debouncer.trigger)
        self.chk_apply_integral = QCheckBox("Apply Integral")
        self.chk_apply_integral.setChecked(signal_config.get("apply_integral", False))
        self.chk_apply_integral.stateChanged.connect(self.debouncer.trigger)
        h3.addWidget(self.chk_freq)
        h3.addWidget(self.chk_time)
        h3.addWidget(self.chk_apply_derivative)
        h3.addWidget(self.chk_apply_integral)
        form.addRow(h3)

        h4 = QHBoxLayout()
        self.combo_signal_display = QComboBox()
        self.combo_signal_display.addItems(
            [
                "Real Part",
                "Imaginary Part",
                "Magnitude",
                "Phase",
            ]
        )
        # Set current index based on config
        display_map = {
            "show_real_part": 0,
            "show_imaginary_part": 1,
            "show_magnitude": 2,
            "show_phase": 3,
        }
        for key, idx in display_map.items():
            if signal_config.get(key, False):
                self.combo_signal_display.setCurrentIndex(idx)
                break
        self.combo_signal_display.currentIndexChanged.connect(self.debouncer.trigger)
        h4.addWidget(QLabel("Signal Display:"))
        h4.addWidget(self.combo_signal_display)
        self.chk_abs = QCheckBox("Show Absolute")
        self.chk_abs.setChecked(signal_config.get("show_absolute", False))
        self.chk_abs.stateChanged.connect(self.debouncer.trigger)
        h4.addWidget(self.chk_abs)
        form.addRow(h4)

        self.filter_band = RangeSlider(Qt.Orientation.Horizontal)
        self.filter_band.setRange(0, 100)
        self.filter_band.setValue(signal_config.get("filter_band"))
        self.filter_band.valueChanged().connect(self.debouncer.trigger)

        self.freq_zoom = RangeSlider(Qt.Orientation.Horizontal)
        self.freq_zoom.setRange(0, 100)
        self.freq_zoom.setValue((0, 100))
        self.freq_zoom.valueChanged().connect(self.debouncer.trigger)

        self.dist_zoom = RangeSlider(Qt.Orientation.Horizontal)
        self.dist_zoom.setRange(0, 100)
        self.dist_zoom.setValue((0, 100))
        self.dist_zoom.valueChanged().connect(self.debouncer.trigger)

        form.addRow(QLabel("Filter Band"), self.filter_band)
        form.addRow(QLabel("Freq Zoom"), self.freq_zoom)
        form.addRow(QLabel("Dist Zoom"), self.dist_zoom)

        params.setLayout(form)
        layout.addWidget(params)

        # Status label to show data loading state
        self.status_label = QLabel(
            "⚠️ No data loaded - please select an input file first"
        )
        self.status_label.setStyleSheet(
            "color: orange; font-weight: bold; padding: 5px;"
        )
        layout.addWidget(self.status_label)

        # Plot area
        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def load_file(self, file_path):
        """Load S-parameter file and update plots"""
        if file_path:
            self.signal_processor = SignalProcessorFactory.create_signal_processor(
                file_path
            )
            success = self.signal_processor.load_network()
            if success:
                self.freq_zoom.setRange(0, 100)
                self.freq_zoom.setValue((0, 100))
                self.dist_zoom.setRange(0, 100)
                self.dist_zoom.setValue((0, 100))
                self._update_widget_states()  # Update widget states after loading
                self.debouncer.trigger()
                return True
            else:
                logging.error("Error loading file: %s", file_path)
                self._update_widget_states()  # Update widget states after failed loading
                return False
        self._update_widget_states()  # Update widget states when no file path
        return False

    def analyze(self):
        """Analyze the loaded signal using the separated signal processor"""
        # Check if data is loaded first
        if not self._is_network_loaded():
            logging.warning("Cannot analyze - no data loaded")
            self._clear_plots()
            return

        try:
            self.save_parameters_to_file()
            parameters = {
                "peak_distance": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.peak_distance"
                ),
                "prominence": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.prominence"
                ),
                "speed": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.speed"
                ),
                "window": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.window"
                ),
                "filter": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.filter"
                ),
                "gating": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.gating"
                ),
                "apply_derivative": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.apply_derivative"
                ),
                "apply_integral": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.apply_integral"
                ),
                "filter_band": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.filter_band"
                ),
                "chosen_signal": self.combo_signal_display.currentText(),
                "show_absolute": self.chk_abs.isChecked(),
            }

            self.signal_processor.run_signal_processing(parameters)

            self._update_plots()

            num_peaks = len(self.signal_processor.peak_indices)
            logging.info("Updated plots - %d peaks detected", num_peaks)

        except Exception as e:
            logging.exception("Error in analysis: %s", e)

    def _update_plots(self):
        """Update the matplotlib plots with current data"""
        try:
            # Get zoom ranges
            f_min, f_max = (
                self.freq_zoom.value()[0] / 100,
                self.freq_zoom.value()[1] / 100,
            )
            d_min, d_max = (
                self.dist_zoom.value()[0] / 100,
                self.dist_zoom.value()[1] / 100,
            )

            self.fig.clf()

            # Frequency domain plot
            if self.chk_freq.isChecked():
                freq_data = self.signal_processor.processed_freq_data
                if freq_data is None:
                    raise ValueError
                ax1 = self.fig.add_subplot(211)
                ax1.plot(freq_data.x, freq_data.y)
                lo, hi = int(f_min * len(freq_data.x)), int(f_max * len(freq_data.x))
                ax1.set_xlim(
                    freq_data.x[lo], freq_data.x[min(hi, len(freq_data.x) - 1)]
                )
                ax1.set_ylabel("Magnitude (dB)")
                ax1.set_title("Frequency Domain")

            # Time domain plot
            if self.chk_time.isChecked():
                td_sig = self.signal_processor.td_filtered
                peaks = self.signal_processor.peaks
                if td_sig is not None:
                    ax2 = self.fig.add_subplot(212)
                    ax2.plot(td_sig.x, td_sig.y)
                    if peaks is not None and len(peaks) > 0:
                        ax2.plot(peaks.x, peaks.y, "rx")
                    lo, hi = int(d_min * len(td_sig.x)), int(d_max * len(td_sig.x))
                    ax2.set_xlim(td_sig.x[lo], td_sig.x[min(hi, len(td_sig.x) - 1)])
                    ax2.set_xlabel("Distance (m)")
                    ax2.set_ylabel("Amplitude")
                    num_peaks = len(peaks) if peaks is not None else 0
                    ax2.set_title(f"Time Domain - {num_peaks} peaks detected")

            self.canvas.draw()

        except Exception as e:
            logging.exception("Error updating plots: %s", e)

    def _clear_plots(self):
        """Clear all plots when no data is loaded"""
        try:
            self.fig.clear()

            # Create empty subplots with helpful messages
            ax1 = self.fig.add_subplot(2, 1, 1)
            ax1.text(
                0.5,
                0.5,
                "No data loaded\nPlease select an input file first",
                ha="center",
                va="center",
                transform=ax1.transAxes,
                fontsize=12,
                color="gray",
            )
            ax1.set_title("Frequency Domain")

            ax2 = self.fig.add_subplot(2, 1, 2)
            ax2.text(
                0.5,
                0.5,
                "No data loaded\nPlease select an input file first",
                ha="center",
                va="center",
                transform=ax2.transAxes,
                fontsize=12,
                color="gray",
            )
            ax2.set_title("Time Domain")

            self.canvas.draw()

        except Exception as e:
            logging.exception("Error clearing plots: %s", e)

    def analyze_and_save(self):
        """Analyze and auto-save parameters (used by explicit save actions)"""
        self.analyze()
        self.save_current_parameters_to_config()

        # Auto-save to file
        try:
            YamlLoader.update_reconstruction_config(self.config)
            YamlLoader.save_reconstruction_config()
            logging.info("Parameters auto-saved to config file")
        except Exception as e:
            logging.warning("Failed to auto-save config: %s", e)

    def get_current_config(self):
        """Get current signal processing configuration"""
        return {
            "peak_distance": self.dist_s.value(),
            "prominence": self.prom_s.value(),
            "speed": self.speed_s.value(),
            "window": self.win_cb.currentText(),
            "filter": self.filter_cb.currentText(),
            "gating": self.gate_le.text(),
            "show_frequency_plot": self.chk_freq.isChecked(),
            "show_distance_plot": self.chk_time.isChecked(),
        }

    def save_current_parameters_to_config(self):
        """Save current signal processing parameters back to config"""
        if "signal_processing_conf" not in self.config:
            self.config["signal_processing_conf"] = {}
        filter_band = self.filter_band.value()
        self.config["signal_processing_conf"].update(
            {
                "peak_distance": self.dist_s.value(),
                "prominence": self.prom_s.value(),
                "speed": self.speed_s.value(),
                "window": self.win_cb.currentText(),
                "filter": self.filter_cb.currentText(),
                "gating": self.gate_le.text(),
                "show_frequency_plot": self.chk_freq.isChecked(),
                "show_distance_plot": self.chk_time.isChecked(),
                "apply_derivative": self.chk_apply_derivative.isChecked(),
                "apply_integral": self.chk_apply_integral.isChecked(),
                "filter_band": list(filter_band),
                "chosen_signal": self.combo_signal_display.currentText(),
                "show_absolute": self.chk_abs.isChecked(),
            }
        )

    def save_parameters_to_file(self):
        """Save current parameters to the YAML configuration file"""
        self.save_current_parameters_to_config()
        try:
            YamlLoader.update_reconstruction_config(self.config)
            YamlLoader.save_reconstruction_config()
            logging.info("Signal processing parameters saved to file")
        except Exception as e:
            logging.error("Failed to save parameters to file: %s", e)


class BasicParametersWidget(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Basic parameters group
        params_group = QGroupBox("Basic Parameters")
        params_layout = QHBoxLayout()

        # File selection - use safe config access
        file_name = YamlLoader.get_safe(
            self.config, "reconstruction_conf.file_name", ""
        )
        self.input_file_selector = InputFileSelector("Input file", file_name)
        params_layout.addWidget(self.input_file_selector)

        # Excitation type - use safe config access
        excitation_layout = QVBoxLayout()
        excitation_layout.addWidget(QLabel("Excitation Type"))
        self.excitation_type = QComboBox()
        self.excitation_type.addItem("Step")
        self.excitation_type.addItem("Impulse")
        excitation_type = YamlLoader.get_safe(
            self.config, "reconstruction_conf.excitation_type", "Step"
        )
        self.excitation_type.setCurrentText(excitation_type)
        excitation_layout.addWidget(self.excitation_type)
        params_layout.addLayout(excitation_layout)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

    def get_current_parameters(self):
        """Get current basic parameters"""
        return {
            "file_name": self.input_file_selector.file_path,
            "excitation_type": self.excitation_type.currentText(),
        }

    def save_current_parameters_to_config(self):
        """Save current basic parameters back to config"""
        if "reconstruction_conf" not in self.config:
            self.config["reconstruction_conf"] = {}

        current_params = self.get_current_parameters()
        self.config["reconstruction_conf"].update(current_params)

    def get_current_config(self):
        """Get the current configuration parameters"""
        self.save_current_parameters_to_config()
        return self.config
