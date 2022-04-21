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
            print(len(self._data))

    def __queryPreprocessor(self, query):
        query = self._normalize(query)
        query = self._tokenize(query)

        has_seen_quote = False
        has_seen_not = False
        exact_seqs = []
        exact_words = []
        match_words = []
        not_words = []
        for word in query:

            if has_seen_quote:
                if word == '"':
                    exact_seqs.append(exact_words)
                    exact_words = []
                else:
                    exact_words.append(self._stem(word))
            else:
                if has_seen_not:
                    has_seen_not = False
                    not_words.append(word)
                else:
                    if word == '!':
                        has_seen_not = True
                    elif word == '"':
                        has_seen_quote = True
                    else:
                        match_words.append(self._stem(word))

        return match_words, not_words, exact_seqs

    def __positionalSearch(self, exact_words):
        docsPosition = {}
        docs = set()
        threshold = len(exact_words)
        for word in exact_words:
            if word in self._dictionary:
                if docsPosition:
                    postings = self._dictionary[word]['postings']
                    for doc_id in postings:
                        if doc_id in docsPosition:
                            prev_positions = docsPosition[doc_id]
                            for pos1 in postings[doc_id]['positions']:
                                for pos2_idx in range(len(prev_positions)):
                                    if pos1 - prev_positions[pos2_idx][-1] == 1:
                                        docsPosition[doc_id][pos2_idx].append(pos1)
                                        if len(docsPosition[doc_id][pos2_idx]) == threshold:
                                            docs.add(doc_id)
                                        break

                else:
                    docsPosition = {}
                    postings = self._dictionary[word]['postings']
                    for doc_id in postings:
                        docsPosition[doc_id] = [[pos] for pos in postings[doc_id]['positions']]
            else:
                return {}

        return docs

    def __querySearch(self, match_words, not_words, exact_seqs):
        # not_docs = set(self._data.keys())
        docs = {}

        # for word in not_words:
        #     if word in self._dictionary:
        #         for doc_id in self._dictionary[word]['postings']:
        #             not_docs.remove(doc_id)

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

        exact_docs = set()
        for exact_words in exact_seqs:
            exact_docs.update(self.__positionalSearch(exact_words))

        final_docs = []
        for doc_id in sorted(docs, key=lambda x: docs[x], reverse=True):
            if doc_id in exact_docs:
                final_docs.append(doc_id)

        return final_docs

    def __show_result(self, docs):
        for doc_id in docs:
            doc = self._data[doc_id]
            print('Title: ', doc['title'])
            print('URL: ', doc['url'])
            print('Content: ', doc['content'])
            print('-------------------------------------------------------------')

    def search(self, query):
        match_words, not_words, exact_seqs = self.__queryPreprocessor(query)
        print(match_words, not_words, exact_seqs)
        docs = self.__querySearch(match_words, not_words, exact_seqs)
        self.__show_result(docs)


def main():
    query_processor = QueryProcessor('../data/dictionary.json', '../data/main_data.json')

    while True:
        query = input('search: ')
        if query == '<off>':
            break
        else:
            query_processor.search(query)
            print()


if __name__ == '__main__':
    main()
