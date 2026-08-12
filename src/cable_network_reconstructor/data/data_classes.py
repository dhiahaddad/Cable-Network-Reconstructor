from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass
class XYData:
    x: np.ndarray
    y: np.ndarray

    def get_subset(self, indices: List[int]) -> "XYData":
        """
        Get a subset of the XYData based on the provided indices.

        Args:
            indices (List[int]): List of indices to select from x and y.

        Returns:
            XYData: A new XYData object containing the selected subset.
        """
        return XYData(x=self.x[indices], y=self.y[indices])

    def __len__(self) -> int:
        """
        Get the length of the x data.

        Returns:
            int: Length of the x data.
        """
        return len(self.x)


@dataclass_json
@dataclass
class TestComparison:
    reference_nodes: List[List[str]]
    reference_loads: List[List[str]]
    to_test_nodes: List[List[str]]
    to_test_loads: List[List[str]]


@dataclass_json
@dataclass
class TestCase:
    test_result: str
    processing_time: float
    test_comparison: TestComparison
    identified_peaks_number: int
    unidentified_peaks_number: int
    peaks_number: int
    is_complete: int
    reconstruction_level: int


@dataclass_json
@dataclass
class Statistics:
    total_tests_number: int
    success_percentage: float
    processing_time: float
    successful_tests_number: int
