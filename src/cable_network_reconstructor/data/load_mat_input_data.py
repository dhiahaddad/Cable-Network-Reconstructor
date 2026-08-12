import copy


def filter_Node_input(model_input_data):
    """Filter input data to get only Node elements."""
    output = []
    for element in model_input_data:
        if len(element) >= 5 and element[4] == "Node":
            data = copy.copy(element)
            data.pop()  # Remove type indicator
            output.append(data)
    return output


def filter_load_input(model_input_data):
    """Filter input data to get only Load elements."""
    output = []
    for element in model_input_data:
        if len(element) >= 5 and element[4] == "Load":
            data = copy.copy(element)
            data.pop()  # Remove type indicator
            output.append(data)
    return output


def filter_fault_input(model_input_data):
    """Filter input data to get only fault elements (Series/Parallel Resistance)."""
    output = []
    for element in model_input_data:
        if len(element) >= 5 and element[4] in [
            "SeriesResistance",
            "ParallelResistance",
        ]:
            data = copy.copy(element)
            output.append(data)  # Keep type indicator for faults
    return output
