import sqlite3
import json
from typing import Any, List

from .data_loader import DataLoader
from .load_mat_input_data import *
from ..network_illustrator import NetworkIllustrator


class SQLInterface:
    def __init__(self, databaseName: str) -> None:
        self.databaseName = databaseName
        self.open_db()

    def open_db(self):
        self.connection = sqlite3.connect(self.databaseName)
        self.cursor = self.connection.cursor()

    def insert_peak(self, time_value: float, amplitude_value: float) -> None:
        self.cursor.execute(
            "INSERT INTO peaks (time, amplitude) VALUES (?, ?)",
            (time_value, amplitude_value),
        )

    def update_mat_input_table(self, file_path) -> None:
        _data_loader = DataLoader()
        junctions_input, loads_input, faults_input = (
            _data_loader.load_and_filter_model_data(file_path)
        )
        for junction in junctions_input:
            self.cursor.execute(
                "INSERT INTO reference_junctions (id, parent_id, distance_to_parent, branches_number) VALUES (?, ?, ?, ?)",
                (junction[0], junction[1], junction[2], junction[3]),
            )
        for load in loads_input:
            self.cursor.execute(
                "INSERT INTO reference_loads (id, parent_id, distance_to_parent, impedance) VALUES (?, ?, ?, ?)",
                (load[0], load[1], load[2], load[3]),
            )
        for fault in faults_input:
            self.cursor.execute(
                "INSERT INTO reference_faults (id, parent_id, distance_to_parent, impedance, fault_type) VALUES (?, ?, ?, ?, ?)",
                (fault[0], fault[1], fault[2], fault[3], fault[4]),
            )

        # Generate and save graph (Todo: take out of here)
        # convert everything to strings
        junctions = [["" for _ in range(4)] for _ in range(len(junctions_input))]
        for i in range(len(junctions_input)):
            for j in range(len(junctions_input[i])):
                junctions[i][j] = str(junctions_input[i][j])
        loads = [["" for _ in range(4)] for _ in range(len(loads_input))]
        for i in range(len(loads_input)):
            for j in range(len(loads_input[i])):
                loads[i][j] = str(loads_input[i][j])
        faults = [["" for _ in range(5)] for _ in range(len(faults_input))]
        for i in range(len(faults_input)):
            for j in range(len(faults_input[i])):
                faults[i][j] = str(faults_input[i][j])

        ni = NetworkIllustrator(junctions, loads, faults)
        ni.create_graph()
        model_name = file_path.split("/")[-1].split(".")[0]
        ni.draw_graph(f"reconstructed_networks/{model_name}_reference")

    def clear_table(self, tableName: str) -> None:
        self.cursor.execute("DELETE FROM " + tableName)
        self.commit()

    def commit(self):
        self.connection.commit()

    def close_db(self) -> None:
        self.connection.close()

    def get_test_cases(self) -> List[Any]:
        self.cursor.execute("SELECT * FROM test_cases")
        rows = self.cursor.fetchall()
        for row in rows:
            for cell in row:
                print(cell, end=" ")
            print()
        return rows

    def get_test_case(self, model_name) -> Any:
        self.cursor.execute(
            "SELECT * FROM test_cases WHERE network_name = '" + model_name + "'"
        )
        rows = self.cursor.fetchall()

        # Generate and save graph
        junctions = self.get_reconstructed_junctions()
        loads = self.get_reconstructed_loads()
        faults = self.get_reconstructed_faults()

        ni = NetworkIllustrator(junctions, loads, faults)
        ni.create_graph()
        ni.draw_graph(f"reconstructed_networks/{model_name}_reconstructed")

        if len(rows) > 0:
            return rows[0]
        else:
            return None

    def get_reconstructed_loads(self):
        self.cursor.execute("SELECT * FROM test_loads")
        loads_str = self.cursor.fetchall()
        loads = [["" for _ in range(4)] for _ in range(len(loads_str))]
        for i in range(len(loads_str)):
            for j in range(len(loads_str[i])):
                loads[i][j] = str(loads_str[i][j])
        return loads

    def get_reconstructed_junctions(self):
        self.cursor.execute("SELECT * FROM test_junctions")
        junctions_str = self.cursor.fetchall()
        junctions = [["" for _ in range(4)] for _ in range(len(junctions_str))]
        for i in range(len(junctions_str)):
            for j in range(len(junctions_str[i])):
                junctions[i][j] = str(junctions_str[i][j])
        return junctions

    def get_reconstructed_faults(self):
        self.cursor.execute("SELECT * FROM test_faults")
        faults_str = self.cursor.fetchall()
        faults = [["" for _ in range(5)] for _ in range(len(faults_str))]
        for i in range(len(faults_str)):
            for j in range(len(faults_str[i])):
                faults[i][j] = str(faults_str[i][j])
        return faults
