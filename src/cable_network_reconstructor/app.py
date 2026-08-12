import random
import re
import sys
import os
from typing import List
import numpy as np

# Add the project root to the path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
if project_root not in sys.path:
    sys.path.append(project_root)

from .common_code.YamlLoader import YamlLoader
from .data.data_classes import Statistics, TestCase, TestComparison, XYData
from .data.load_signal_data import get_test_case
from .data.sql_interface import SQLInterface
from .utils.generate_existing_models_names import filter_network_model_names
from .signal_processor import SignalProcessorFactory
from cpp.binaries import CppToPython  # type: ignore[reportMissingImports]


class App:

    _initial_path_length: int = 0
    _file_name: str = ""
    _model_name: str = ""
    _peak_height: float = 0.0
    _tests_number: int = 25
    _parent_folder: str = ""
    _model_names: List[str] = []
    _reconstruction_level: int = 1
    _min_complexity_input: int = 1
    _max_complexity_input: int = 1
    _detect_soft_faults: bool = False
    _excitation_type: str = "step"
    _peaks: XYData = XYData(np.array([]), np.array([]))

    def __init__(self):
        self.plot_x = 230
        self.plot_y = 80
        self.plot_width = 550
        self.plot_height = 400

        self.model_names = []
        self._num_files_input = 0

        self.config = YamlLoader.get_reconstruction_config()

        self.prefill_variables()

    def update_conf_file(self):
        self.config["reconstruction_conf"] = dict()
        self.config["reconstruction_conf"]["file_name"] = self._file_name
        self.config["reconstruction_conf"]["path_length"] = self._initial_path_length
        self.config["reconstruction_conf"]["peak_height"] = self._peak_height
        self.config["reconstruction_conf"]["level"] = self._reconstruction_level
        self.config["plot_conf"] = dict()
        self.config["plot_conf"]["x"] = self.plot_x
        self.config["plot_conf"]["y"] = self.plot_y
        self.config["plot_conf"]["width"] = self.plot_width
        self.config["plot_conf"]["height"] = self.plot_height
        self.config["reconstruction_conf"]["parent_folder"] = self._parent_folder
        self.config["reconstruction_conf"][
            "min_complexity"
        ] = self._min_complexity_input
        self.config["reconstruction_conf"][
            "max_complexity"
        ] = self._max_complexity_input
        self.config["reconstruction_conf"]["tests_number"] = self._tests_number
        self.config["reconstruction_conf"][
            "detect_soft_faults"
        ] = self._detect_soft_faults
        self.config["reconstruction_conf"]["excitation_type"] = self._excitation_type
        YamlLoader.update_reconstruction_config(self.config)
        YamlLoader.save_reconstruction_config()

    def prefill_variables(self) -> None:
        try:
            config = YamlLoader.get_reconstruction_config()

            self._initial_path_length = int(
                YamlLoader.get_safe(config, "reconstruction_conf.path_length", 15)
            )
            self._peak_height = float(
                YamlLoader.get_safe(config, "reconstruction_conf.peak_height", 0.01)
            )
            self._file_name = YamlLoader.get_safe(
                config, "reconstruction_conf.file_name", ""
            )
            self.plot_x = YamlLoader.get_safe(config, "plot_conf.x", self.plot_x)
            self.plot_y = YamlLoader.get_safe(config, "plot_conf.y", self.plot_y)
            self.plot_width = YamlLoader.get_safe(
                config, "plot_conf.width", self.plot_width
            )
            self.plot_height = YamlLoader.get_safe(
                config, "plot_conf.height", self.plot_height
            )
            self._parent_folder = YamlLoader.get_safe(
                config, "reconstruction_conf.parent_folder", ""
            )
            self._min_complexity_input = YamlLoader.get_safe(
                config, "reconstruction_conf.min_complexity", 1
            )
            self._max_complexity_input = YamlLoader.get_safe(
                config, "reconstruction_conf.max_complexity", 1
            )
            self._tests_number = YamlLoader.get_safe(
                config, "reconstruction_conf.tests_number", 25
            )
            self._detect_soft_faults = YamlLoader.get_safe(
                config, "reconstruction_conf.detect_soft_faults", False
            )
            self._excitation_type = YamlLoader.get_safe(
                config, "reconstruction_conf.excitation_type", "step"
            )

        except Exception as ex:
            print(f"Error loading configuration: {ex}")

    def receive_data(self, data: XYData):
        self._peaks = data
        print(f"Received data with {len(data.x)} points.")

    def run_single_test(self) -> None:
        self._reconstruction_level = 1
        dbi: SQLInterface = SQLInterface("database.db")
        dbi.clear_table("test_cases")
        dbi.commit()
        dbi.close_db()
        self.update_conf_file()
        # gaussian_chirp_peak_extraction_function_mat(self._file_name, '/home/dhia/reconstructioncpp/ChirpModels/excitation.mat', self.app._peak_height)
        dbi.open_db()
        dbi.clear_table("peaks")
        for i in range(1, len(self._peaks)):
            dbi.insert_peak((self._peaks.x[i] - self._peaks.x[0]), self._peaks.y[i])
        dbi.clear_table("reference_loads")
        dbi.clear_table("reference_junctions")
        dbi.clear_table("reference_faults")
        dbi.update_mat_input_table(self._file_name)
        dbi.commit()
        dbi.close_db()
        self._model_name = f"{self._file_name.split('.mat')[0].split('/')[-1]}"

        if not self._model_name or self._model_name.strip() == "":
            print("Error: Model name is empty or None")
            return

        print(self._model_name)
        CppToPython.py_main()
        # test_result_idx = 2
        # test_result = test_case_statistics[test_result_idx]
        is_complete_idx = 8
        test_case_statistics = get_test_case(self._model_name)

        if test_case_statistics is None:
            print(f"Warning: No test case found for model: {self._model_name}")
            return

        if len(test_case_statistics) <= is_complete_idx:
            print(
                f"Warning: Test case statistics incomplete for model: {self._model_name}"
            )
            return

        is_complete = test_case_statistics[is_complete_idx]
        if is_complete == "0":
            self._reconstruction_level += 1
            self.run_next_level_test()
            test_case_statistics = get_test_case(self._model_name)

            if (
                test_case_statistics is None
                or len(test_case_statistics) <= is_complete_idx
            ):
                print(
                    f"Warning: Test case still incomplete after next level test for model: {self._model_name}"
                )
                return

            is_complete = test_case_statistics[is_complete_idx]
            if is_complete == "0":
                self._reconstruction_level += 1
                self.run_next_level_test()

    def run_random_tests(self, min_cplxity: int, max_cplxity: int):
        print("============================================================")
        print("============================================================")
        self._reconstruction_level = 1
        dbi: SQLInterface = SQLInterface("database.db")
        dbi.clear_table("test_cases")
        dbi.commit()
        dbi.close_db()
        models = filter_network_model_names(
            self._parent_folder,
            rf"Model_[{min_cplxity}-{max_cplxity}]+_([1-9]|[1-9][0-9])_([1-9]|[1-9][0-9])+\.mat",
        )
        tests_number = min(self._tests_number, len(models))
        self.model_names = random.sample(models, tests_number)
        self.model_names.sort()
        print(self.model_names)
        for model_name in self.model_names:
            self._reconstruction_level = 1
            self._file_name = self._parent_folder + "/" + model_name
            self.update_conf_file()
            processor = SignalProcessorFactory.create_signal_processor(self._file_name)
            processor.load_network()
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
                "chosen_signal": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.chosen_signal"
                ),
                "show_absolute": YamlLoader.get_safe(
                    self.config, "signal_processing_conf.show_absolute"
                ),
            }

            processor.run_signal_processing(parameters)
            # processor.peaks_from_model_to_db()
            # gaussian_chirp_peak_extraction_function_mat(self._file_name, '/home/dhia/reconstructioncpp/NoisyChirpModels/excitation.mat', self._peak_height)
            dbi.open_db()
            dbi.clear_table("reference_loads")
            dbi.clear_table("reference_junctions")
            dbi.clear_table("reference_faults")
            dbi.update_mat_input_table(self._file_name)
            dbi.commit()
            dbi.close_db()
            print(model_name)
            CppToPython.py_single_test()
            test_result_idx = 2
            is_complete_idx = 8
            test_case_statistics = get_test_case(model_name)
            test_result = test_case_statistics[test_result_idx]
            is_complete = test_case_statistics[is_complete_idx]
            if is_complete == "0":
                self._reconstruction_level = 2
                self.run_next_level_test()
                test_case_statistics = get_test_case(model_name)
                is_complete = test_case_statistics[is_complete_idx]
                if is_complete == "0":
                    self._reconstruction_level = 3
                    self.run_next_level_test()

    def set_parameters(
        self, path_length: int, peak_height: float, detect_soft_faults: bool
    ) -> None:
        self._initial_path_length = path_length
        self._peak_height = peak_height
        self._detect_soft_faults = detect_soft_faults

    def set_multi_rec_parameters(
        self, tests_number: int, min_complexity_input: int, max_complexity_input: int
    ) -> None:
        self._tests_number = tests_number
        self._min_complexity_input = min_complexity_input
        self._max_complexity_input = max_complexity_input
        self._num_files_input = tests_number

    def run_next_level_test(self):
        self.update_conf_file()
        processor = SignalProcessorFactory.create_signal_processor(self._file_name)
        processor.load_network()
        parameters = {
            "peak_distance": YamlLoader.get_safe(
                self.config, "signal_processing_conf.peak_distance"
            ),
            "prominence": YamlLoader.get_safe(
                self.config, "signal_processing_conf.prominence"
            ),
            "speed": YamlLoader.get_safe(self.config, "signal_processing_conf.speed"),
            "window": YamlLoader.get_safe(self.config, "signal_processing_conf.window"),
            "filter": YamlLoader.get_safe(self.config, "signal_processing_conf.filter"),
            "gating": YamlLoader.get_safe(self.config, "signal_processing_conf.gating"),
            "apply_derivative": YamlLoader.get_safe(
                self.config, "signal_processing_conf.apply_derivative"
            ),
            "apply_integral": YamlLoader.get_safe(
                self.config, "signal_processing_conf.apply_integral"
            ),
            "filter_band": YamlLoader.get_safe(
                self.config, "signal_processing_conf.filter_band"
            ),
            "chosen_signal": YamlLoader.get_safe(
                self.config, "signal_processing_conf.chosen_signal"
            ),
            "show_absolute": YamlLoader.get_safe(
                self.config, "signal_processing_conf.show_absolute"
            ),
        }

        processor.run_signal_processing(parameters)
        # processor.peaks_from_model_to_db()
        # gaussian_chirp_peak_extraction_function_mat(self._file_name, '/home/dhia/reconstructioncpp/ChirpModels/excitation.mat', self._peak_height)
        print("=================> LEVEL " + str(self._reconstruction_level))
        dbi: SQLInterface = SQLInterface("database.db")
        dbi.open_db()
        dbi.clear_table("reference_loads")
        dbi.clear_table("reference_junctions")
        dbi.clear_table("reference_faults")
        dbi.update_mat_input_table(self._file_name)
        dbi.commit()
        dbi.close_db()
        CppToPython.py_single_test()

    def run_all_level_two_tests(self):
        additional_successful_networks = 0
        self._reconstruction_level += 1
        for model_name in self.model_names:
            test_case_statistics = get_test_case(model_name)
            if test_case_statistics != None:
                test_result_idx = 2
                is_complete_idx = 8
                test_result = test_case_statistics[test_result_idx]
                is_complete = test_case_statistics[is_complete_idx]
                if is_complete == "0":  # TODO
                    self._file_name = self._parent_folder + "/" + model_name
                    self.run_next_level_test()

    def set_file_name(self, file_path: str) -> None:
        self._file_name = file_path
        self._parent_folder, _sep, _after = file_path.rpartition("/")
        self._model_name = file_path.split("/")[-1].split(".")[0]

    def get_test_case_result(self, model_name) -> TestCase:
        test_case_statistics = get_test_case(model_name)

        if test_case_statistics is None:
            print(f"Warning: No test case found for model: {model_name}")
            test_comparison = TestComparison([], [], [], [])
            return TestCase("0", 0.0, test_comparison, 0, 0, 0, 0, 0)

        for cell in test_case_statistics:
            print(cell, end=" ")
        print()

        # Check if we have enough data
        required_indices = [2, 3, 5, 6, 7, 8, 9]  # All indices we need
        if len(test_case_statistics) <= max(required_indices):
            print(f"Warning: Incomplete test case data for model: {model_name}")
            test_comparison = TestComparison([], [], [], [])
            return TestCase("0", 0.0, test_comparison, 0, 0, 0, 0, 0)

        test_comparison = TestComparison([], [], [], [])
        test_result_idx = 2
        processing_time_idx = 3
        identified_peaks_number_idx = 5
        unidentified_peaks_number_idx = 6
        total_peaks_number_idx = 7
        is_complete_idx = 8
        reconstruction_level_idx = 9
        test_case = TestCase(
            test_case_statistics[test_result_idx],
            test_case_statistics[processing_time_idx],
            test_comparison,
            test_case_statistics[identified_peaks_number_idx],
            test_case_statistics[unidentified_peaks_number_idx],
            test_case_statistics[total_peaks_number_idx],
            test_case_statistics[is_complete_idx],
            test_case_statistics[reconstruction_level_idx],
        )
        return test_case

    def get_statistics(self) -> Statistics:
        dbi: SQLInterface = SQLInterface("database.db")
        test_result_idx = 2
        processing_time_idx = 3
        test_cases = dbi.get_test_cases()
        total_tests_number: int = len(test_cases)
        succeeded_tests_number: int = 0
        processing_time: float = 0
        for test_case in test_cases:
            processing_time += test_case[processing_time_idx]
            succeeded_tests_number += int(test_case[test_result_idx])
        success_percentage: float = (
            succeeded_tests_number / total_tests_number
        ) * 100.0
        statistics = Statistics(
            total_tests_number,
            success_percentage,
            processing_time,
            succeeded_tests_number,
        )
        return statistics
