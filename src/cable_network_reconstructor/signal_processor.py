"""
Signal Processing Module

This module contains the core signal processing functionality separated from GUI concerns.
It handles S-parameter analysis, time-domain conversion, peak detection, and filtering.
Supports S-parameter files (.s1p, .s2p), CSV files, and MATLAB files (.mat).

Now integrates with the DataLoader class for unified file loading.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import skrf as rf
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt, find_peaks, windows

from .data.data_classes import XYData
from .data.data_loader import DataLoader


class SignalProcessorFactory:
    """
    Factory class to create SignalProcessor instances.
    This allows for easy extension and modification of signal processing behavior.
    """

    @staticmethod
    def create_signal_processor(file_path: str) -> "SignalProcessor":
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension in [".s1p", ".s2p"]:
                return FreqDomSignalProcessor(file_path)
            if file_extension in [".csv", ".mat"]:
                return TimeDomSignalProcessor(file_path)
            logging.error("Unsupported file format: %s", file_extension)
            return None

        except (ValueError, FileNotFoundError, OSError) as e:
            logging.error("Error loading file: %s", e)
            return None


class SignalProcessor(ABC):
    file_path: str
    time_data: XYData | None = None
    freq_data: XYData | None = None
    distance_data: XYData | None = None
    td_gated: XYData | None = None
    td_filtered: XYData | None = None
    freq: np.ndarray | None = None
    chosen_fd_values: np.ndarray | None = None
    processed_freq_data: XYData | None = None
    peak_indices: np.ndarray | None = None
    peaks: XYData | None = None
    gating: str | None = None
    filter_type: str | None = None
    peak_distance: float | None = None
    prominence: float | None = None
    speed: float | None = None
    window_type: str | None = None
    apply_derivative: bool | None = None
    apply_integral: bool | None = None
    filter_band: float | None = None
    chosen_signal: str | None = None
    show_absolute: bool | None = None
    freq_real: XYData | None
    freq_imag: XYData | None
    freq_mag: XYData | None
    freq_phase: XYData | None
    data_loader: DataLoader

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data_loader = DataLoader()

    def get_time_data(self) -> XYData | None:
        """
        Get the time domain data.

        Returns:
            Time domain data as XYData object or None if not available
        """
        return self.time_data

    def get_freq_data(self) -> XYData | None:
        """
        Get the frequency domain data.

        Returns:
            Frequency domain data as XYData object or None if not available
        """
        return self.freq_data

    def get_peak_indices(self) -> np.ndarray | None:
        """
        Get the peak indices.

        Returns:
            Array of peak indices or None if not available
        """
        return self.peak_indices

    def get_peaks(self) -> XYData | None:
        """
        Get the peak data.

        Returns:
            Peak data as XYData object or None if not available
        """
        return self.peaks

    @abstractmethod
    def load_network(self) -> bool:
        pass

    @abstractmethod
    def process_signal(self) -> None:
        """
        Process the signal data.

        This method should be implemented by subclasses to handle specific file formats.
        """

    def run_signal_processing(self, parameters: dict[str, Any]) -> None:
        self.peak_distance = parameters.get("peak_distance")
        self.prominence = parameters.get("prominence")
        self.speed = parameters.get("speed")
        self.window_type = parameters.get("window")
        self.filter_type = parameters.get("filter")
        self.gating = parameters.get("gating")
        self.apply_derivative = parameters.get("apply_derivative")
        self.apply_integral = parameters.get("apply_integral")
        self.filter_band = parameters.get("filter_band")
        self.chosen_signal = parameters.get("chosen_signal")
        self.show_absolute = parameters.get("show_absolute")
        self.process_signal()

    def _apply_gating(self):
        """
        Apply distance gating to the time domain signal.

        Args:
            td: Time domain signal
            distance_array: Corresponding distance array
            gating: Gating range as string "start:end"

        Returns:
            Gated time domain signal
        """
        if self.gating == "0:0":
            self.td_gated = self.distance_data
            return

        try:
            gate_start, gate_end = map(float, self.gating.split(":"))
            gate_mask = (self.distance_data.x >= gate_start) & (
                self.distance_data.x <= gate_end
            )
            self.td_gated = self.distance_data.get_subset(gate_mask)
        except (ValueError, AttributeError) as e:
            logging.warning("Invalid gating format '%s': %s", self.gating, e)
            self.td_gated = self.distance_data

    def _apply_filtering(self) -> None:
        """
        Apply filtering to the time domain signal.

        Args:
            td: Time domain signal
            filter_type: Type of filter ("None", "Lowpass", "Highpass", "Bandpass")

        Returns:
            Filtered time domain signal
        """
        if self.filter_type == "None":
            self.td_filtered = self.td_gated
            return

        try:
            # Determine sampling rate from x-axis (distance or time)
            if self.td_gated is None:
                raise ValueError
            if len(self.td_gated.x) > 1:
                sample_spacing = self.td_gated.x[1] - self.td_gated.x[0]
                fs = 1.0 / sample_spacing
            else:
                fs = 1.0

            if self.filter_type == "Lowpass":
                Wn = self.filter_band[1] / (fs / 2)
                b, a = butter(4, Wn, btype="low")
            elif self.filter_type == "Highpass":
                Wn = self.filter_band[0] / (fs / 2)
                b, a = butter(4, Wn, btype="high")
            elif self.filter_type == "Bandpass":
                Wn = [self.filter_band[0] / (fs / 2), self.filter_band[1] / (fs / 2)]
                b, a = butter(4, Wn, btype="band")
            else:
                raise ValueError(f"Unknown filter type: {self.filter_type}")

            # Apply filter to real and imaginary parts separately
            if np.iscomplexobj(self.td_gated.y):
                real_part = np.real(self.td_gated.y)
                imag_part = np.imag(self.td_gated.y)
                td_real_filtered = filtfilt(b, a, real_part)
                td_imag_filtered = filtfilt(b, a, imag_part)
                self.td_filtered = XYData(
                    x=self.td_gated.x, y=td_real_filtered + 1j * td_imag_filtered
                )
            else:
                self.td_filtered = XYData(
                    x=self.td_gated.x, y=filtfilt(b, a, self.td_gated.y)
                )
        except (ValueError, TypeError) as e:
            logging.warning("Error applying filter '%s': %s", self.filter_type, e)
            self.td_filtered = self.td_gated  # Fallback to gated data

    def _find_peak_indices(self) -> None:
        if self.td_filtered is None:
            raise ValueError
        try:
            # Convert distance threshold to sample distance
            if len(self.td_filtered.x) > 1:
                distance_step = self.td_filtered.x[1] - self.td_filtered.x[0]
                min_sample_distance = max(1, int(self.peak_distance / distance_step))
            else:
                min_sample_distance = 1

            # Find peaks in magnitude
            self.peak_indices, _ = find_peaks(
                np.abs(self.td_filtered.y),
                distance=min_sample_distance,
                prominence=self.prominence,
            )
        except (ValueError, TypeError) as e:  # type: ignore[misc]
            logging.warning("Error finding peaks: %s", e)
            self.peak_indices = np.array([])

    def _prepare_multiple_freq_representations(self) -> None:
        """
        Prepare multiple representations of frequency domain data.
        """
        if self.freq_data is None:
            return
        if self.chosen_signal == "Real Part":
            self.chosen_fd_values = np.real(self.freq_data.y)
        elif self.chosen_signal == "Imaginary Part":
            self.chosen_fd_values = np.imag(self.freq_data.y)
        elif self.chosen_signal == "Magnitude":
            self.chosen_fd_values = np.abs(self.freq_data.y)
        elif self.chosen_signal == "Phase":
            self.chosen_fd_values = np.angle(self.freq_data.y, deg=True)
        else:
            self.chosen_fd_values = self.freq_data.y
        if self.show_absolute:
            self.chosen_fd_values = np.abs(self.chosen_fd_values)

    def resample_data(self, data: XYData, fixed_time_step: float) -> XYData:
        """
        Resample data to a fixed time step using linear interpolation.

        Args:
            data: Input data to resample
            fixed_time_step: Fixed time step for resampling

        Returns:
            XYData with resampled data
        """
        new_time = np.arange(min(data.x), max(data.x), fixed_time_step)
        interp_func = interp1d(
            data.x, data.y, kind="linear", fill_value=0, bounds_error=False
        )
        new_amplitude = interp_func(new_time)
        return XYData(new_time, new_amplitude)

    def get_differential(self, data: XYData) -> XYData:
        """
        Calculate the differential of signal data.

        Args:
            data: Input signal data

        Returns:
            XYData containing differential data
        """
        array_peaks_x_diff = data.x
        array_peaks_y_diff = np.diff(data.y)
        array_peaks_y_diff = np.insert(array_peaks_y_diff, 0, 0)
        return XYData(array_peaks_x_diff, array_peaks_y_diff)

    def get_integral(self, data: XYData) -> XYData:
        """
        Calculate the integral of signal data.

        Args:
            data: Input signal data

        Returns:
            XYData containing integral data
        """
        array_peaks_x_int = data.x
        array_peaks_y_int = np.cumsum(data.y) * (
            data.x[1] - data.x[0]
        )  # Assuming uniform spacing
        return XYData(array_peaks_x_int, array_peaks_y_int)

    def get_frequency_data(self) -> XYData:
        return self.freq_data


class TimeDomSignalProcessor(SignalProcessor):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.raw_data = None

    def load_network(self):
        try:
            self.raw_data = self.data_loader.load_signal_data(self.file_path)
            logging.info(
                "Loaded time-domain file: %s with %d data points",
                self.file_path,
                len(self.raw_data.x),
            )
            return True
        except (ValueError, FileNotFoundError, KeyError) as e:
            logging.error("Error loading time-domain file: %s", e)
            return False

    def process_signal(self) -> None:
        """Process time-domain data from CSV/MAT files."""
        if self.raw_data is None:
            raise ValueError("No time-domain data loaded")

        # Extract time and amplitude data
        time_axis = self.raw_data.x
        amplitude_data = self.raw_data.y

        distance_data = XYData(time_axis * self.speed, amplitude_data)
        new_distance_step = 0.001  # TODO: make this configurable
        self.distance_data = self.resample_data(distance_data, new_distance_step)
        time_array = self.distance_data.x / self.speed
        self.time_data = XYData(time_array, self.distance_data.y)

        if self.apply_derivative:
            self.distance_data = self.get_differential(self.distance_data)
        if self.apply_integral:
            self.distance_data = self.get_integral(self.distance_data)
        self._apply_gating()
        self._apply_filtering()
        self._find_peak_indices()
        self.peaks = self.td_filtered.get_subset(self.peak_indices)

        # For time-domain data, create a synthetic frequency array for compatibility
        if len(time_axis) > 1:
            fft_data = np.fft.fft(amplitude_data)
            time_step = time_axis[1] - time_axis[0]
            self.freq = np.fft.fftfreq(len(time_axis), d=time_step)
            # Take only positive frequencies
            positive_freq_indices = self.freq >= 0
            self.freq = self.freq[positive_freq_indices]
            fft_data = fft_data[positive_freq_indices]
        else:
            self.freq = np.array([])
            fft_data = np.array([])

        self.freq_data = XYData(self.freq, fft_data)
        self._prepare_multiple_freq_representations()
        self.processed_freq_data = XYData(self.freq, self.chosen_fd_values)


class FreqDomSignalProcessor(SignalProcessor):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.ntwk = None
        self.freq = None  # Frequency array in GHz

    def load_network(self) -> bool:
        try:
            self.ntwk = rf.Network(self.file_path)
            logging.info(
                "Loaded S-parameter file: %s with %d frequency points",
                self.file_path,
                len(self.ntwk.f),
            )
            return True
        except (ValueError, OSError, KeyError) as e:
            logging.error("Error loading S-parameter file: %s", e)
            return False

    def process_signal(self) -> None:
        """Process S-parameter data (existing logic)."""
        if self.ntwk is None:
            raise ValueError(
                "No S-parameter network loaded. Call load_network() first."
            )

        # Get S11 parameter
        s11 = self.ntwk.s[:, 0, 0]
        self.freq = self.ntwk.f  # Frequency in Hz
        self.freq_data = XYData(self.freq, s11)
        self._prepare_multiple_freq_representations()
        self.processed_freq_data = XYData(self.freq, self.chosen_fd_values)

        # Apply windowing and convert to time domain
        window_func = getattr(windows, self.window_type)
        windowed_s11 = self.chosen_fd_values * window_func(len(self.chosen_fd_values))
        td = (
            np.fft.ifft(windowed_s11, n=2 * len(windowed_s11)) * 100
        )  # TODO scaling factor

        # Create time and distance arrays
        if self.freq is not None and len(self.freq) > 1:
            freq_step = self.freq[1] - self.freq[0]
        else:
            raise ValueError("Invalid frequency data")

        t = np.fft.fftfreq(len(td), d=freq_step)

        positive_indices = t >= 0
        t = t[positive_indices]
        td = td[positive_indices]

        distance_array = t * self.speed

        self.time_data = XYData(t, td)
        self.distance_data = XYData(distance_array, td)
        if self.apply_derivative:
            self.distance_data = self.get_differential(self.distance_data)
        if self.apply_integral:
            self.distance_data = self.get_integral(self.distance_data)
        self._apply_gating()
        self._apply_filtering()
        self._find_peak_indices()
        self.peaks = self.td_filtered.get_subset(self.peak_indices)
