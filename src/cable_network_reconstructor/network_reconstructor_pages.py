from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QGroupBox,
    QLabel,
)
from PySide6.QtCore import Signal
import logging

from .data.data_classes import XYData

from .common_code.common_qt_widgets import (
    PageTitleWidget,
    PushButton,
    InputField_QSpinBox,
    CheckBox,
)
from .common_code.YamlLoader import YamlLoader
from .network_reconstructor_widgets import (
    MultiTest,
    MultiTestInputs,
    SingleTest,
    SignalProcessingWidget,
    BasicParametersWidget,
)
from .app import App


class ReconstructionInputPage(QWidget):
    data_emitted = Signal(XYData)

    def __init__(self, parent=None):
        super(ReconstructionInputPage, self).__init__(parent)
        self.config = YamlLoader.get_reconstruction_config()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        title = PageTitleWidget("Network Reconstructor - Signal Analysis")
        layout.addWidget(title)

        # 1. Basic Parameters Widget (file input and basic reconstruction parameters)
        self.basicParametersWidget = BasicParametersWidget(self.config, self)
        layout.addWidget(self.basicParametersWidget)

        # 2. Signal Processing Widget
        self.signalProcessingWidget = SignalProcessingWidget(self.config, self)
        layout.addWidget(self.signalProcessingWidget)

        # Connect file selection from basic parameters to signal processing
        self.setup_widget_connections()

        # 3. Save and Continue Button
        element_height = self.height() * 0.1
        self.save_and_continue_btn = PushButton(
            "Save Parameters and Continue", element_height
        )
        self.save_and_continue_btn.clicked.connect(self.save_parameters_and_continue)
        layout.addWidget(self.save_and_continue_btn)

        # Back button
        self.back_btn = PushButton("Back to Home Page", element_height)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def setup_widget_connections(self):
        """Connect the file selection from basic parameters to signal processing"""
        if hasattr(self.basicParametersWidget, "input_file_selector") and hasattr(
            self.basicParametersWidget.input_file_selector, "run_analysis_btn"
        ):
            # Connect the analysis button to load file in signal processing widget
            self.basicParametersWidget.input_file_selector.run_analysis_btn.clicked.connect(
                self.trigger_signal_analysis
            )

    def trigger_signal_analysis(self):
        """Trigger signal analysis with the currently selected file"""
        if (
            hasattr(self.basicParametersWidget, "input_file_selector")
            and self.basicParametersWidget.input_file_selector.file_path
        ):
            file_path = self.basicParametersWidget.input_file_selector.file_path
            self.signalProcessingWidget.load_file(file_path)

    def save_parameters_and_continue(self):
        """Save both basic parameters and signal processing parameters"""
        self.basicParametersWidget.save_current_parameters_to_config()
        self.signalProcessingWidget.save_current_parameters_to_config()

        self._save_config_to_file()

        self.data_emitted.emit(self.signalProcessingWidget.signal_processor.peaks)

        # Navigate to next page (this will be handled by parent widget)
        print("Parameters saved successfully!")

    def update_config(self):
        """Update configuration with current parameters"""
        self.basicParametersWidget.save_current_parameters_to_config()
        self.signalProcessingWidget.save_current_parameters_to_config()
        # Update the static configuration
        YamlLoader.update_reconstruction_config(self.config)

    def _save_config_to_file(self):
        """Save the current configuration to the YAML file"""
        try:
            YamlLoader.update_reconstruction_config(self.config)
            YamlLoader.save_reconstruction_config()
            logging.info("Configuration saved to file successfully")
        except Exception as e:
            logging.error("Failed to save configuration to file: %s", e)


class ReconstructionTestConfigPage(QWidget):
    def __init__(self, parent=None):
        super(ReconstructionTestConfigPage, self).__init__(parent)
        self.config = YamlLoader.get_reconstruction_config()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        title = PageTitleWidget("Network Reconstructor - Test Configuration")
        layout.addWidget(title)

        self.setup_test_params(layout)
        self.setup_action_buttons(layout)
        element_height = self.height() * 0.1
        self.back_btn = PushButton("Back to Signal Analysis", element_height)
        layout.addWidget(self.back_btn)

        # Multi-test parameters (hidden by default, shown when "Run Multiple Tests" is clicked)
        self.multiTestInputs = MultiTestInputs(self.config)
        self.multiTestInputs.setVisible(False)
        layout.addWidget(self.multiTestInputs)

        self.setLayout(layout)

    def setup_test_params(self, parent_layout):
        """Setup test parameters"""
        params_group = QGroupBox("Test Parameters")
        params_layout = QHBoxLayout()

        # Detect soft faults
        self.detect_soft_faults = CheckBox("Detect Soft Faults")
        detect_soft_faults = YamlLoader.get_safe(
            self.config, "reconstruction_conf.detect_soft_faults", False
        )
        self.detect_soft_faults.setChecked(detect_soft_faults)
        params_layout.addWidget(self.detect_soft_faults)

        # Path length
        self.path_length_input = InputField_QSpinBox("Path Length")
        path_length = YamlLoader.get_safe(
            self.config, "reconstruction_conf.path_length", 15
        )
        self.path_length_input.setValue(int(path_length))
        params_layout.addWidget(self.path_length_input)

        params_group.setLayout(params_layout)
        parent_layout.addWidget(params_group)

    def setup_action_buttons(self, parent_layout):
        """Setup action buttons"""
        buttons_group = QGroupBox("Run Tests")
        buttons_layout = QHBoxLayout()

        self.run_single_test_btn = PushButton("Run Single Test", 60)
        self.run_multiple_tests_btn = PushButton("Run Multiple Tests", 60)

        buttons_layout.addWidget(self.run_single_test_btn)
        buttons_layout.addWidget(self.run_multiple_tests_btn)

        buttons_group.setLayout(buttons_layout)
        parent_layout.addWidget(buttons_group)

    def get_current_config(self):
        """Get current test configuration"""
        return {
            "detect_soft_faults": self.detect_soft_faults.checkBox.isChecked(),
            "path_length": self.path_length_input.input_field.value(),
        }

    def update_config(self):
        YamlLoader.ensure_section_exists(self.config, "reconstruction_conf")

        test_config = self.get_current_config()

        if "detect_soft_faults" in test_config:
            self.config["reconstruction_conf"]["detect_soft_faults"] = test_config[
                "detect_soft_faults"
            ]
        if "path_length" in test_config:
            self.config["reconstruction_conf"]["path_length"] = test_config[
                "path_length"
            ]

        if self.multiTestInputs.isVisible():
            self.config["reconstruction_conf"][
                "min_complexity"
            ] = self.multiTestInputs.min_complexity_input.input_field.value()
            self.config["reconstruction_conf"][
                "max_complexity"
            ] = self.multiTestInputs.max_complexity_input.input_field.value()
            self.config["reconstruction_conf"][
                "tests_number"
            ] = self.multiTestInputs.num_files_input.input_field.value()

        # Update the static configuration
        YamlLoader.update_reconstruction_config(self.config)
        logging.info("Test configuration updated successfully")

    def show_multi_test_options(self):
        """Show multi-test parameters when 'Run Multiple Tests' is clicked"""
        self.multiTestInputs.setVisible(True)

    def hide_multi_test_options(self):
        """Hide multi-test parameters"""
        self.multiTestInputs.setVisible(False)


class ReconstructionSingleTestPage(QWidget):
    def __init__(self, app: App, parent=None):
        super(ReconstructionSingleTestPage, self).__init__(parent)
        self.config = YamlLoader.get_reconstruction_config()
        self.app = app
        self.initUI()

    def initUI(self):
        self.singleTestLayout = SingleTest()
        element_height = self.height() * 0.1
        self.back_btn = PushButton("Back to Input Page", element_height)

        layout = QVBoxLayout()
        title = PageTitleWidget("Network Reconstructor")
        layout.addWidget(title)

        layout.addLayout(self.singleTestLayout)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def run_test(self):
        file_path = YamlLoader.get_safe(
            self.config, "reconstruction_conf.file_name", ""
        )
        path_length = int(
            YamlLoader.get_safe(self.config, "reconstruction_conf.path_length", 15)
        )
        peak_threshold = float(
            YamlLoader.get_safe(self.config, "reconstruction_conf.peak_height", 0.01)
        )
        detect_soft_faults = bool(
            YamlLoader.get_safe(
                self.config, "reconstruction_conf.detect_soft_faults", False
            )
        )

        self.app.set_file_name(file_path)
        self.app.set_parameters(path_length, peak_threshold, detect_soft_faults)
        self.app.run_single_test()

        test_case = self.app.get_test_case_result(self.app._model_name)
        self.singleTestLayout.update_figures(
            self.app._parent_folder, self.app._model_name
        )
        self.singleTestLayout.update_test_case_results(test_case)

    def showEvent(self, event):
        # Code to run when this page is opened
        self.run_test()
        super().showEvent(event)


class ReconstructionMultiTestPage(QWidget):
    def __init__(self, app: App, parent=None):
        super(ReconstructionMultiTestPage, self).__init__(parent)
        self.config = YamlLoader.get_reconstruction_config()
        self.app = app
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        title = PageTitleWidget("Network Reconstructor")
        layout.addWidget(title)
        self.multiTest = MultiTest()
        layout.addWidget(self.multiTest)

        self.singleTestLayout = SingleTest()
        layout.addLayout(self.singleTestLayout)

        element_height = self.height() * 0.1
        self.back_btn = PushButton("Back to Input Page", element_height)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def run_test(self):
        file_path = YamlLoader.get_safe(
            self.config, "reconstruction_conf.file_name", ""
        )
        path_length = int(
            YamlLoader.get_safe(self.config, "reconstruction_conf.path_length", 15)
        )
        peak_threshold = float(
            YamlLoader.get_safe(self.config, "reconstruction_conf.peak_height", 0.01)
        )
        detect_soft_faults = bool(
            YamlLoader.get_safe(
                self.config, "reconstruction_conf.detect_soft_faults", False
            )
        )
        min_complexity_input = int(
            YamlLoader.get_safe(self.config, "reconstruction_conf.min_complexity", 2)
        )
        max_complexity_input = int(
            YamlLoader.get_safe(self.config, "reconstruction_conf.max_complexity", 6)
        )
        tests_number = int(
            YamlLoader.get_safe(self.config, "reconstruction_conf.tests_number", 50)
        )

        self.app.set_file_name(file_path)
        self.app.set_parameters(path_length, peak_threshold, detect_soft_faults)
        self.app.set_multi_rec_parameters(
            tests_number, min_complexity_input, max_complexity_input
        )
        self.app.run_random_tests(min_complexity_input, max_complexity_input)

        self.multiTest.dropdown_menu.clear()
        model_names = self.app.model_names
        model_names.sort()
        self.multiTest.dropdown_menu.addItems(model_names)
        self.singleTestLayout.update_figures(
            self.app._parent_folder, self.app._model_name
        )
        test_case = self.app.get_test_case_result(self.app._model_name)
        self.singleTestLayout.update_test_case_results(test_case)

        statistics = self.app.get_statistics()
        self.multiTest.update_statistics(statistics)

    def showEvent(self, event):
        # Code to run when this page is opened
        self.run_test()
        super().showEvent(event)
