import urllib.request
import json
import codecs

class DownloadJSON():
    def __init__(self, urls, names, path):
        self.urls = urls
        self.names = names
        self.path = path
        if len(urls) != len(names):
            raise Exception('Неккоректные входные данные')

    def download(self):
        for i in range(len(self.urls)):
            self.__download_json(self.urls[i], self.names[i])

    def __download_json(self, url, name):
        with urllib.request.urlopen(url) as urlb:
            data = json.load(urlb)
            json.dump(data, codecs.open(self.path + name, 'w', 'utf-8'), indent=2, ensure_ascii=False)