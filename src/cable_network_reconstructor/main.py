import sys

from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from .app import App
from .common_code.home_page import HomePage
from .common_code.YamlLoader import YamlLoader
from .network_reconstructor_pages import (
    ReconstructionInputPage,
    ReconstructionMultiTestPage,
    ReconstructionSingleTestPage,
    ReconstructionTestConfigPage,
)


class CableDiagnosisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load configurations using static methods
        self.reconstruction_config = YamlLoader.load_reconstruction_config()
        self.reconstruction_config = YamlLoader.validate_and_fix_config(self.reconstruction_config)
        YamlLoader.update_reconstruction_config(self.reconstruction_config)
            
        self.app = App()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Cable Diagnosis Prototype")
        self.setGeometry(100, 100, 1500, 1200)

        icon_path = "Logo-MST.ico"
        self.setWindowIcon(QtGui.QIcon(icon_path)) # didn't work in wsl. didn't try windows

        # Stacked Widget to hold different pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Initialize pages
        self.home_page = HomePage()
        self.input_page = ReconstructionInputPage()
        self.test_config_page = ReconstructionTestConfigPage()
        self.single_test_page = ReconstructionSingleTestPage(self.app)
        self.multi_test_page = ReconstructionMultiTestPage(self.app)

        # Connect buttons to navigation methods
        self.home_page.reconstrBtn.clicked.connect(self.show_input_page)
        
        # Connect enhanced interface buttons
        self.input_page.save_and_continue_btn.clicked.connect(self.show_test_config_page)
        self.input_page.data_emitted.connect(self.app.receive_data)
        self.test_config_page.run_single_test_btn.clicked.connect(self.show_single_test_page)
        self.test_config_page.run_multiple_tests_btn.clicked.connect(self.handle_multiple_tests)
        self.test_config_page.multiTestInputs.run_random_tests_btn.clicked.connect(self.show_multi_test_page)
        self.input_page.back_btn.clicked.connect(self.show_home_page)
        self.test_config_page.back_btn.clicked.connect(self.show_input_page)
        self.single_test_page.back_btn.clicked.connect(self.show_test_config_page)
        self.multi_test_page.back_btn.clicked.connect(self.show_test_config_page)
        self.multi_test_page.multiTest.dropdown_menu.currentIndexChanged.connect(self.show_selected_network_results)

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.input_page)
        self.stacked_widget.addWidget(self.test_config_page)
        self.stacked_widget.addWidget(self.single_test_page)
        self.stacked_widget.addWidget(self.multi_test_page)

        self.show_home_page()
        # self.show_input_page()

    def show_home_page(self):
        self.setStyleSheet("background-color: white;")
        self.stacked_widget.setCurrentWidget(self.home_page)

    def show_input_page(self):
        self.setStyleSheet("")
        self.stacked_widget.setCurrentWidget(self.input_page)

    def show_test_config_page(self):
        self.setStyleSheet("")
        
        try:
            self.input_page.update_config()
        except Exception as e:
            print(f"Warning: Error updating config from input page: {e}")
        
        self.stacked_widget.setCurrentWidget(self.test_config_page)

    def show_single_test_page(self):
        self.setStyleSheet("")
        try:
            self.test_config_page.update_config()
        except Exception as e:
            print(f"Warning: Error updating config from test config page: {e}")
            
        self.test_config_page.hide_multi_test_options()  # Hide multi-test options when running single test
        self.stacked_widget.setCurrentWidget(self.single_test_page)

    def handle_multiple_tests(self):
        """Handle the 'Run Multiple Tests' button click"""
        self.test_config_page.show_multi_test_options()  # Show multi-test parameters
        
    def show_multi_test_page(self):
        self.setStyleSheet("")
        try:
            self.test_config_page.update_config()
        except Exception as e:
            print(f"Warning: Error updating config from test config page: {e}")
            
        self.stacked_widget.setCurrentWidget(self.multi_test_page)

    def run_next_level_test(self):
        # Placeholder for the next level test logic
        pass

    def show_selected_network_results(self, index):
        if index == -1:
            return
        selected_network = self.multi_test_page.multiTest.dropdown_menu.itemText(index)
        self.app._model_name = selected_network
        self.multi_test_page.singleTestLayout.update_figures(self.app._parent_folder, self.app._model_name)
        test_case = self.app.get_test_case_result(selected_network)
        self.multi_test_page.singleTestLayout.update_test_case_results(test_case)

def main() -> None:
    app = QApplication(sys.argv)
    ex = CableDiagnosisGUI()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
