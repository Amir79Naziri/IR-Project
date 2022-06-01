from phaseOne import setup
import json
from math import log2, log10, sqrt, pow


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
        exact_seqs = []
        exact_words = []
        match_words = []
        not_words = []
        for word in query:

            if has_seen_quote:
                if word == '"':
                    exact_seqs.append(exact_words)
                    exact_words = []
                    has_seen_quote = False
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

    def __positionalSearch(self, exact_words, docs):
        docsPosition = {}

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
                                            exact_seq = ' '.join(exact_words)
                                            if doc_id in docs:
                                                if exact_seq in docs[doc_id]['exact_words']:
                                                    docs[doc_id]['exact_words'][exact_seq] += 1
                                                else:
                                                    docs[doc_id]['exact_words'][exact_seq] = 1

                                        break

                else:
                    docsPosition = {}
                    postings = self._dictionary[word]['postings']
                    for doc_id in postings:
                        docsPosition[doc_id] = [[pos] for pos in postings[doc_id]['positions']]
            else:
                return

    def __querySearch(self, match_words, not_words, exact_seqs):

        docs = {}
        for doc_id in self._data:
            docs[doc_id] = {'exact_words': {}, 'match_words': {}}

        for word in not_words:
            if word in self._dictionary:
                for doc_id in self._dictionary[word]['postings']:
                    if doc_id in docs:
                        docs.pop(doc_id)

        for word in match_words:
            if word in self._dictionary:
                for doc_id in self._dictionary[word]['postings']:
                    if doc_id in docs:
                        if word in docs[doc_id]['match_words']:
                            docs[doc_id]['match_words'][word] += self._dictionary[word][doc_id]['count']
                        else:
                            docs[doc_id]['match_words'][word] = \
                                self._dictionary[word]['postings'][doc_id]['count']

        if match_words:
            for doc_id in docs.copy():
                if len(docs[doc_id]['match_words']) == 0:
                    docs.pop(doc_id)

        for exact_words in exact_seqs:
            self.__positionalSearch(exact_words, docs)

        if exact_seqs:
            for doc_id in docs.copy():
                if len(docs[doc_id]['exact_words']) != len(exact_seqs):
                    docs.pop(doc_id)

        return docs

    def __rank(self, docs, match_words, exact_seqs):
        max_dict = {}

        for word in match_words:
            if word in self._dictionary:
                max_dict[word] = self._dictionary[word]['count']

        for exact_words in exact_seqs:
            min_count = 0
            add = True
            for word in exact_words:
                if word in self._dictionary:
                    min_count = min(min_count, self._dictionary[word]['count'])
                else:
                    add = False
                    break
            if add:
                max_dict[' '.join(exact_words)] = min_count

        for doc_id in docs:
            rank_val = 0
            for exact_words in exact_seqs:
                if ' '.join(exact_words) in max_dict:
                    rank_val += log2((docs[doc_id]['exact_words'].get(' '.join(exact_words), 0) + 0.01)
                                     / (max_dict[' '.join(exact_words)] + 0.01))

            for word in match_words:
                if word in max_dict:
                    rank_val += log2((docs[doc_id]['match_words'].get(word, 0) + 0.01)
                                     / (max_dict[word] + 0.01))

            docs[doc_id]['rank'] = rank_val
        # print(docs)
        return sorted(docs, key=lambda x: docs[x]['rank'], reverse=True)

    def __cosine_score(self, match_words):
        repeat_per_word = {}
        for term in match_words:
            if term in repeat_per_word:
                repeat_per_word[term] += 1
            else:
                repeat_per_word[term] = 1
        # print(repeat_per_word)
        score = {}
        length = {}
        for term in match_words:
            if term in self._dictionary:
                w_tq = 1 + log10(repeat_per_word[term])
                for doc_per_term in self._dictionary[term]['champion_list']:
                    w_td = self._dictionary[term]['postings'][str(doc_per_term)]['tf_idf']
                    if doc_per_term in score:
                        score[str(doc_per_term)] += w_td * w_tq
                    else:
                        score[str(doc_per_term)] = w_td * w_tq

                    if doc_per_term in length:
                        length[str(doc_per_term)] += pow(w_td, 2)
                    else:
                        length[str(doc_per_term)] = pow(w_td, 2)

        for doc in score:
            score[doc] = score[doc] / sqrt(length[doc])

        return sorted(score, key=lambda x: score[x], reverse=True)

    def __show_result(self, docs, limit=5):
        items = 0
        for doc_id in docs:
            doc = self._data[doc_id]
            print('ID', doc_id)
            print('Title: ', doc['title'])
            print('URL: ', doc['url'])
            # print('Content: ', doc['content'])
            print()
            items += 1
            if items == limit:
                break

    def search(self, query, tf_idf=False):
        match_words, not_words, exact_seqs = self.__queryPreprocessor(query)
        # print(match_words, not_words, exact_seqs)
        if tf_idf:
            sorted_docs = self.__cosine_score(match_words)
        else:
            docs = self.__querySearch(match_words, not_words, exact_seqs)
            sorted_docs = self.__rank(docs, match_words, exact_seqs)
        self.__show_result(sorted_docs)


def main(dictionary_url, data_url):
    query_processor = QueryProcessor(dictionary_url, data_url)

    while True:
        query = input('search: ')
        if query == '<off>':
            break
        else:
            query_processor.search(query, True)


if __name__ == '__main__':
    main('../data/dictionary_tf_idf_champion.json', '../data/IR_data_news_12k.json')
