import json
from ..data import Statistics, TestCase
from typing import List


def write_json_statistics( statistics:Statistics):

    with open(f"results//statistics.json", "w") as outfile:
        # json_object = json.dumps(statistics.to_json())
        json_object = dict(total_tests_number = statistics.total_tests_number, success_percentage = statistics.success_percentage, processing_time = statistics.processing_time)
        print(str(json_object))
        outfile.write(str(json_object).replace("'", '"'))

def write_json_test_cases(model_name, test_case:TestCase):

    with open(f"results//{model_name}.json", "w") as outfile:
        # json_object = json.dumps(test_case.to_json())
        test_comparison = test_case.test_comparison
        json_object = dict(test_result = test_case.test_result, test_comparison = test_case.test_comparison, processing_time = test_case.processing_time)
        outfile.write(str(json_object).replace("'", '"').replace("TestComparison(","").replace(")", "").replace("reference_nodes", '{ "reference_nodes"').replace(', "processing_time"', '}, "processing_time"').replace("=",":").replace("reference_loads",'"reference_loads"').replace("to_test_nodes",'"to_test_nodes"').replace("to_test_loads",'"to_test_loads"'))


def read_json_statistics():

    with open(f"results//statistics.json") as file:
        json_object = json.load(file)
        print("Type:", type(json_object))
        statistics = Statistics(json_object["total_tests_number"], json_object["success_percentage"], json_object["processing_time"]) 
    return statistics

def read_json_test_case(model_name):

    with open(f"results//{model_name}.json") as file:
        json_object = json.load(file)
        testcase = TestCase(json_object["test_result"], json_object["processing_time"], json_object["test_comparison"])
    return testcase