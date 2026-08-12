import csv


def write_csv_model_names(model_names):

    with open("results//Tested_model_names.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Model number", "Model name"])
        for model_number, model_name in enumerate(model_names):
            writer.writerow([(model_number + 1), model_name])


def read_csv_model_names():
    tested_model_names = []

    with open("results//Tested_model_names.csv") as file:
        csv_reader = csv.reader(file)
        for line, raw in enumerate(csv_reader):
            if line == 0:
                pass
            else:
                tested_model_names.append(raw[1])

    return tested_model_names
