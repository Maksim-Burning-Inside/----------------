from get_data import DownloadJSON
from preprocess_raw_data import CreateEviedenceData
from get_coref_and_dep_data import DependenciesСoreferences

if __name__ == '__main__':
    urls = ['http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_train_v1.1.json', 'http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json']
    DownloadJSON_input = ['train.json', 'valid.json']
    data_path = 'databases/'

    DownloadJSON(urls, DownloadJSON_input, data_path).download()
    CreateEviedenceData(data_path).create_clean_data()
    DependenciesСoreferences(data_path).build()