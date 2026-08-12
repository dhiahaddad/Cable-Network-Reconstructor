"""
DataLoader Class Module

This module provides a unified DataLoader class that handles loading of various file formats
including S-parameter files (.s1p, .s2p), CSV files, and MATLAB files (.mat).

The DataLoader class provides a consistent interface for all file loading operations
and integrates with the existing data processing pipeline.
"""

import logging
import os
from typing import Any

import numpy as np
import pandas as pd
import scipy.io

from .data_classes import XYData

try:
    import skrf as rf
except ImportError:
    rf = None


class DataLoader:
    """
    Unified data loader class for handling various file formats.

    Supports:
    - S-parameter files (.s1p, .s2p) using scikit-rf
    - CSV files with time-domain data
    - MATLAB files (.mat) with signal data
    - MATLAB input files (_input.mat) with network topology
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_signal_data(self, file_path: str) -> XYData:
        """
        Load signal data from various file formats.

        Args:
            file_path: Path to the input file

        Returns:
            XYData: Loaded signal data

        Raises:
            ValueError: If file format is unsupported
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()
        self.logger.info("Loading file with extension: %s", file_extension)

        if file_extension == ".mat":
            return self._load_mat_signal_data(file_path)
        elif file_extension == ".csv":
            return self._load_csv_data(file_path)
        elif file_extension in [".s1p", ".s2p"]:
            return self._load_s_parameter_data(file_path)
        else:
            # Try auto-detection
            return self._auto_detect_and_load(file_path)

    def _load_mat_signal_data(self, file_path: str) -> XYData:
        """Load signal data from MATLAB .mat file."""
        try:
            file = scipy.io.loadmat(file_path)
            data = file["output"]
            data_x = np.squeeze(data[:, 0])
            data_y = np.squeeze(data[:, 1])
            self.logger.info("Loaded MAT file: %d data points", len(data_x))
            return XYData(x=data_x, y=data_y)
        except Exception as e:
            raise ValueError(f"Failed to load MAT file {file_path}: {e!s}") from e

    def _load_csv_data(self, file_path: str) -> XYData:
        """Load signal data from CSV file."""
        try:
            df = pd.read_csv(
                file_path, skiprows=6, delimiter=",", decimal=".", header=0
            )
            time: pd.Series = pd.to_numeric(df["Time(s)"], errors="coerce")
            s11: pd.Series = pd.to_numeric(df["S11(REAL)"], errors="coerce")

            # Drop rows where either value is NaN
            mask = time.notna() & s11.notna()

            self.logger.info("Loaded CSV file: %d valid data points", mask.sum())
            return XYData(np.asarray(time[mask]), np.asarray(s11[mask]))
        except Exception as e:
            raise ValueError(f"Failed to load CSV file {file_path}: {e!s}") from e

    def _load_s_parameter_data(self, file_path: str) -> XYData:
        """Load S-parameter data from .s1p or .s2p files."""
        if rf is not None:
            try:
                # Use scikit-rf for robust S-parameter loading
                network = rf.Network(file_path)
                freq = network.frequency.f  # frequency in Hz
                s_param = network.s[:, 0, 0]  # S11 parameter
                s_db = 20 * np.log10(np.abs(s_param))

                self.logger.info(
                    "Loaded S-parameter file: %d frequency points", len(freq)
                )
                return XYData(x=freq, y=s_db)
            except (ValueError, OSError, KeyError) as e:
                self.logger.warning(
                    "scikit-rf loading failed, trying text format: %s", e
                )
                return self._load_s_parameter_text_format(file_path)
        else:
            return self._load_s_parameter_text_format(file_path)

    def _load_s_parameter_text_format(self, file_path: str) -> XYData:
        """Fallback function to load S-parameter files in text format."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Skip comment lines and parse numerical data
            data_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("!") and not line.startswith("#"):
                    if not any(
                        line.upper().startswith(keyword)
                        for keyword in ["# HZ", "# GHZ", "# MHZ", "# KHZ"]
                    ):
                        data_lines.append(line)

            frequencies = []
            s11_real = []
            s11_imag = []

            for line in data_lines:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        freq = float(parts[0])
                        real_part = float(parts[1])
                        imag_part = float(parts[2])

                        frequencies.append(freq)
                        s11_real.append(real_part)
                        s11_imag.append(imag_part)
                    except ValueError:
                        continue

            if not frequencies:
                raise ValueError("No valid numerical data found in S-parameter file")

            # Convert to complex numbers and then to magnitude in dB
            s11_complex = np.array(s11_real) + 1j * np.array(s11_imag)
            s11_db = 20 * np.log10(np.abs(s11_complex))

            self.logger.info(
                "Loaded S-parameter text file: %d frequency points", len(frequencies)
            )
            return XYData(x=np.array(frequencies), y=s11_db)

        except Exception as e:
            raise ValueError(
                f"Failed to load S-parameter file {file_path}: {e!s}"
            ) from e

    def _auto_detect_and_load(self, file_path: str) -> XYData:
        """Try to auto-detect file format and load."""
        # Try CSV first, then S-parameter format
        try:
            return self._load_csv_data(file_path)
        except (
            ValueError,
            FileNotFoundError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ):
            try:
                return self._load_s_parameter_data(file_path)
            except Exception as exc:
                raise ValueError(
                    f"Could not determine file format for: {file_path}"
                ) from exc

    def load_model_input(self, file_path: str = "Model_1") -> list[list[Any]]:
        """
        Load network topology data from MATLAB input file.

        Args:
            file_path: Base path for the model (without _input.mat suffix)

        Returns:
            List of network elements with their properties
        """
        # Construct input file path
        input_file_path = f"{file_path.split('.mat')[0]}_input.mat"

        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")

        try:
            file = scipy.io.loadmat(input_file_path)
            data = file["input_data"]
            output = []

            for element in data:
                output_element = []
                element_type = int(element[4])

                if element_type == 0:  # Node
                    output_element.extend(
                        [
                            str(int(element[0])),
                            str(int(element[1])),
                            round(element[2], 3),
                            int(element[3]),
                            "Node",
                        ]
                    )
                elif element_type == 1:  # Load
                    output_element.extend(
                        [
                            str(int(element[0])),
                            str(int(element[1])),
                            str(round(element[2], 3)),
                            float(element[3]),
                            "Load",
                        ]
                    )
                elif element_type == 2:  # Parallel Resistance
                    output_element.extend(
                        [
                            str(int(element[0])),
                            str(int(element[1])),
                            str(round(element[2], 3)),
                            float(element[3]),
                            "ParallelResistance",
                        ]
                    )
                elif element_type == 3:  # Series Resistance
                    output_element.extend(
                        [
                            str(int(element[0])),
                            str(int(element[1])),
                            str(round(element[2], 3)),
                            float(element[3]),
                            "SeriesResistance",
                        ]
                    )

                output.append(output_element)

            self.logger.info("Loaded model input: %d elements", len(output))
            return output

        except Exception as e:
            raise ValueError(
                f"Failed to load model input from {input_file_path}: {e!s}"
            ) from e

    def load_and_filter_model_data(
        self, file_path: str = "Model_1"
    ) -> tuple[list, list, list]:
        """
        Load model input data and filter into nodes, loads, and faults.

        Args:
            file_path: Base path for the model

        Returns:
            Tuple of (nodes, loads, faults) lists
        """
        data = self.load_model_input(file_path)

        nodes = []
        loads = []
        faults = []

        for element in data:
            if len(element) >= 5:
                element_type = element[4]

                if element_type == "Node":
                    node_data = element[:-1]  # Remove type indicator
                    nodes.append(node_data)
                elif element_type == "Load":
                    load_data = element[:-1]  # Remove type indicator
                    loads.append(load_data)
                elif element_type in ["SeriesResistance", "ParallelResistance"]:
                    faults.append(element)  # Keep type indicator for faults

        self.logger.info(
            "Filtered model data: %d nodes, %d loads, %d faults",
            len(nodes),
            len(loads),
            len(faults),
        )
        return nodes, loads, faults

    @staticmethod
    def get_supported_formats() -> list[str]:
        """Get list of supported file formats."""
        return [".s1p", ".s2p", ".csv", ".mat"]

    def validate_file(self, file_path: str) -> bool:
        """
        Validate if file can be loaded.

        Args:
            file_path: Path to file

        Returns:
            bool: True if file can be loaded
        """
        if not os.path.exists(file_path):
            return False

        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.get_supported_formats()
