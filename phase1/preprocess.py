from hazm import *
import json


class Preprocess:
    def __init__(self):
        self.__normalize = Normalizer().normalize
        self.__stem = Stemmer().stem
        self.__tokenize = word_tokenize
        self.__data = {}

    def __init_data(self, raw_data_url):
        with open(raw_data_url, 'r') as f:
            data = json.load(f)
            total = len(data)
            print("loading data ...")
            print('|', end='')
            for idx in data.keys():
                self.__data[int(idx)] = {'title': data[f'{idx}']['title'],
                                  'url': data[f'{idx}']['url'],
                                  'content': data[f'{idx}']['content']}


                if int(idx) % 200 == 0:
                    print('=', end='')

            print('|')

    def __save_data(self, new_data_url):
        print('saving data ...')
        with open(new_data_url, 'w') as f:
            f.write(json.dumps(self.__data))

    def __preprocess(self):
        print('preprocess data ...')
        print('|', end='')
        for idx in range(len(self.__data)):
            content = self.__normalize(self.__data[idx]['content'])
            content = self.__tokenize(content)
            for word_idx in range(len(content)):
                content[word_idx] = self.__stem(content[word_idx])

            self.__data[idx]['content'] = content

            if idx % 200 == 0:
                print('=', end='')
        print('|')

    def start(self, raw_data_url, new_data_url):
        self.__init_data(raw_data_url)
        self.__preprocess()
        self.__save_data(new_data_url)
        print('done.')


if __name__ == '__main__':
    preprocessor = Preprocess()
    preprocessor.start('../data/IR_data_news_12k.json', '../data/main_data.json')

