from phaseOne import setup
import json


class QueryProcessor(setup.Setup):
    def __init__(self, dictionary_url, docs_url):
        super().__init__()
        self.__load_processor(dictionary_url, docs_url)

    def __load_processor(self, dictionary_url, data_url):
        print("initializing query processor ...")
        with open(dictionary_url, 'r') as f:
            self._dictionary = json.load(f)
        with open(data_url, 'r') as f:
            self._data = json.load(f)

    def __queryPreprocessor(self, query):
        query = self._normalize(query)
        query = self._tokenize(query)

        has_seen_quote = False
        has_seen_not = False
        exact_words = []
        exact_word = []
        match_words = []
        not_words = []
        for word in query:

            if has_seen_quote:
                if word == '«' or word == '»':
                    exact_words.append(exact_word)
                    exact_word = []
                else:
                    exact_word.append(self._stem(word))
            else:
                if has_seen_not:
                    has_seen_not = False
                    not_words.append(word)
                else:
                    if word == '!':
                        has_seen_not = True
                    elif word == '«' or word == '»':
                        has_seen_quote = True
                    else:
                        match_words.append(self._stem(word))

        return match_words, not_words, exact_words

    def __querySearch(self, match_words, not_words, exact_words):
        docs = {}

        for word in match_words:
            if word in self._dictionary:
                for doc in self._dictionary[word]['postings']:
                    if doc in docs:
                        docs[doc] += 1
                    else:
                        docs[doc] = 0

        for word in not_words:
            if word in self._dictionary:
                for doc in self._dictionary[word]['postings']:
                    if doc in docs:
                        docs.pop(doc)

        docs = sorted(docs, key=lambda x: docs[x], reverse=True)
        return docs

    def __show_result(self, docs):
        for doc_id in docs:
            doc = self._data[doc_id]
            print('Title: ', doc['title'])
            print('URL: ', doc['url'])
            print('Content: ', doc['content'])
            print('-------------------------------------------------------------')
            break

    def search(self, query):
        match_words, not_words, exact_words = self.__queryPreprocessor(query)
        docs = self.__querySearch(match_words, not_words, exact_words)
        self.__show_result(docs)


def main():
    query_processor = QueryProcessor('../data/dictionary.json', '../data/IR_data_news_12k.json')
    # query_processor.search('تحریم های !آمریکا "علیه ایران"')

    while True:
        query = input('search: ')
        if query == '<off>':
            break
        else:
            query_processor.search(query)
            print()


if __name__ == '__main__':
    main()
    # a = {'1': 8, '2': 12, '5': 3}
    # b = {'2': 7, '1': 1}
    # # for i in b:
    # #     if i in a:
    # #         a.pop(i)
    # print(sorted(a, key=lambda x: a[x], reverse=True))