from hazm import *
import json
import string


class Preprocess:
    def __init__(self):
        self.__normalize = Normalizer().normalize
        self.__stem = Stemmer().stem
        self.__tokenize = word_tokenize
        self.__data = {}
        self.__dictionary = {}
        self.__punctuations = ''.join(set(list(string.punctuation + '~`$^\,÷×.:،_-/٪%؛؟?!()[]«»…@#&*+=|<>')))

    def __init_data(self, raw_data_url):
        print("loading data ...")
        with open(raw_data_url, 'r') as f:
            data = json.load(f)
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
            content = self.__normalize(self.__data[idx]['content'][:-15])
            content = self.__tokenize(content)
            final_content = []
            for word_idx in range(len(content)):
                if content[word_idx] not in self.__punctuations:
                    stemmed_word = self.__stem(content[word_idx])
                    final_content.append(stemmed_word)
                    if stemmed_word in self.__dictionary.keys():
                        self.__dictionary[stemmed_word] += 1
                    else:
                        self.__dictionary[stemmed_word] = 0

            self.__data[idx]['content'] = final_content

            if idx % 400 == 0:
                print('=', end='')

    def __delete_stopwords(self):
        for idx in range(len(self.__data)):
            final_content = []
            for word_idx in range(len(self.__data[idx]['content'])):
                if self.__dictionary[self.__data[idx]['content'][word_idx]] <= 22368:
                    final_content.append(self.__data[idx]['content'][word_idx])

            self.__data[idx]['content'] = final_content
            if idx % 400 == 0:
                print('=', end='')
        print('|')

    def start(self, raw_data_url, new_data_url):
        self.__init_data(raw_data_url)
        self.__preprocess()
        self.__delete_stopwords()
        self.__save_data(new_data_url)
        print('done.')

    def data(self):
        return self.__data



if __name__ == '__main__':
    # preprocessor = Preprocess()
    # preprocessor.start('../data/IR_data_news_12k.json', '../data/main_data.json')

    # with open('../data/main_data.json', 'r') as f:
    #     data = json.load(f)
    #     print(data["0"]["content"])
    #
    # with open('../data/IR_data_news_12k.json', 'r') as f:
    #     data = json.load(f)
    #     print(data["0"]["content"])
    pass
