import os
import re

def main():

    print(filter_network_model_names("Model_[0-9]+\.mat"))


def get__all_files_names(path):

    return  os.listdir(path)


def filter_names(regex:str, text:str):

    return re.search(regex,text)


def filter_network_model_names(parent_folder, regex):
    model_names = []
    entries = get__all_files_names(parent_folder)
    for entrie in entries:
        result = filter_names(regex,entrie)
        if result != None:
            model_names.append(result.group().removesuffix('.mat')) 
    return model_names


if __name__ == '__main__':

    main()



