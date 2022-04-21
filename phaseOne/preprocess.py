from phaseOne import setup
import json
import string
from stopwordsiso import stopwords


class Preprocess(setup.Setup):
    def __init__(self):
        super().__init__()
        self.__punctuations = ''.join(set(list(string.punctuation + '~`$^\,÷×.:،_-/٪%؛؟?!()[]«»…@#&*+=|<>')))
        self.__stop_words = stopwords('fa')

    def __init_data(self, raw_data_url):
        print("loading data ...")
        with open(raw_data_url, 'r') as f:
            data = json.load(f)
            print('|', end='')
            for idx in data.keys():
                self._data[int(idx)] = {'title': data[f'{idx}']['title'],
                                        'url': data[f'{idx}']['url'],
                                        'content': data[f'{idx}']['content']}

                if int(idx) % 200 == 0:
                    print('=', end='')

            print('|')

    def __save_data(self, new_data_url):
        print('saving data ...')
        with open(new_data_url, 'w') as f:
            f.write(json.dumps(self._data))

    def __preprocess(self):
        print('preprocess data ...')
        print('|', end='')
        for idx in range(len(self._data)):
            content = self._normalize(self._data[idx]['content'][:-15])
            content = self._tokenize(content)
            final_content = []
            for word_idx in range(len(content)):
                if content[word_idx] not in self.__punctuations:
                    stemmed_word = self._stem(content[word_idx])
                    final_content.append(stemmed_word)
                    # if stemmed_word in self._dictionary.keys():
                    #     self._dictionary[stemmed_word] += 1
                    # else:
                    #     self._dictionary[stemmed_word] = 1

            self._data[idx]['content'] = final_content

            if idx % 400 == 0:
                print('=', end='')

    def __delete_stopwords(self):

        for idx in range(len(self._data)):
            final_content = []
            for word_idx in range(len(self._data[idx]['content'])):
                # if self._dictionary[self._data[idx]['content'][word_idx]] <= 22368:
                if not(self._data[idx]['content'][word_idx] in self.__stop_words):
                    final_content.append(self._data[idx]['content'][word_idx])

            self._data[idx]['content'] = final_content
            if idx % 400 == 0:
                print('=', end='')
        print('|')

    def start(self, raw_data_url, new_data_url):
        self.__init_data(raw_data_url)
        self.__preprocess()
        self.__delete_stopwords()
        self.__save_data(new_data_url)
        print('done.')


if __name__ == '__main__':
    preprocessor = Preprocess()
    preprocessor.start('../data/IR_data_news_12k.json', '../data/main_data.json')
