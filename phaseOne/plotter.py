import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import json


def zipf_plot(with_stopwords_dictionary_url, without_stopwords_dictionary_url):
    print("loading data ...")

    with open(with_stopwords_dictionary_url, 'r') as f:
        data1 = json.load(f)
    with open(without_stopwords_dictionary_url, 'r') as f:
        data2 = json.load(f)

    print('plotting ...')

    sorted_data1 = sorted(data1, key=lambda x: data1[x]['count'], reverse=True)
    sorted_data2 = sorted(data2, key=lambda x: data2[x]['count'], reverse=True)

    k1 = data1[sorted_data1[0]]['count']
    k2 = data2[sorted_data2[0]]['count']

    rank1 = np.arange(1, len(sorted_data1) + 1, step=1)
    rank2 = np.arange(1, len(sorted_data2) + 1, step=1)

    x1 = np.log10(rank1)
    x2 = np.log10(rank2)

    estimated_y1 = np.log10(k1) - x1
    estimated_y2 = np.log10(k2) - x2

    real_y1 = np.log10(np.array([data1[sorted_data1[i]]['count'] for i in range(0, len(sorted_data1))]))
    real_y2 = np.log10(np.array([data2[sorted_data2[i]]['count'] for i in range(0, len(sorted_data2))]))

    fig, ax = plt.subplots(1, 2)

    ax[0].plot(x1, estimated_y1, label='estimated cf')
    ax[0].plot(x1, real_y1, label='real cf')

    ax[1].plot(x2, estimated_y2, label='estimated cf')
    ax[1].plot(x2, real_y2, label='real cf')

    plt.sca(ax[0])
    plt.legend()
    plt.xlabel('log10  rank')
    plt.ylabel('log10  cf')
    plt.title('with stopwords')

    plt.sca(ax[1])
    plt.legend()
    plt.xlabel('log10  rank')
    plt.ylabel('log10  cf')
    plt.title('without stopwords')

    plt.show()


def heap_plot(dictionary_urls, main_dictionary, title):

    def numberOfTokens(dictionary):
        tokens = 0
        for k in dictionary:
            tokens += int(dictionary[k]['count'])
        return tokens

    def vocabSize(dictionary):
        return len(dictionary)

    x = []
    y = []

    print("loading data ...")
    for key in dictionary_urls:
        with open(dictionary_urls[key], 'r') as f:
            d = json.load(f)
            x.append(numberOfTokens(d))
            y.append(vocabSize(d))

    with open(main_dictionary, 'r') as f:
        d = json.load(f)
        main_tokens = numberOfTokens(d)
        main_vocabSize = vocabSize(d)

    x = np.log10(np.array(x))
    y = np.log10(np.array(y))

    print('fitting ...')

    def heapLaw(T, b, k):
        return b * T + np.log10(k)

    params, _ = curve_fit(heapLaw, x, y)

    print('plotting ...')

    plt.plot(x, y, label='real')
    plt.plot(x, heapLaw(x, *params), label='estimated')
    plt.xlabel('log10 T')
    plt.ylabel('log10 M')
    plt.suptitle(title)
    plt.title('b = {:.4} , k = {:.4}'.format(*params))
    plt.legend()
    plt.show()

    print('real dictionary size:', main_vocabSize)
    print('estimated dictionary size:', int(10 ** heapLaw(np.log10(main_tokens), *params)))



if __name__ == '__main__':
    # zipf_plot('../data/dictionary_with_stopwords.json', '../data/dictionary.json')

    no_stemmed = {'500': '../data/dictionary_500_no_stemmed.json',
                  '1000': '../data/dictionary_1000_no_stemmed.json',
                  '1500': '../data/dictionary_1500_no_stemmed.json',
                  '2000': '../data/dictionary_2000_no_stemmed.json'}

    stemmed = {'500': '../data/dictionary_500_stemmed.json',
               '1000': '../data/dictionary_1000_stemmed.json',
               '1500': '../data/dictionary_1500_stemmed.json',
               '2000': '../data/dictionary_2000_stemmed.json'}

    heap_plot(stemmed, '../data/dictionary.json', 'stemmed')
    # heap_plot(no_stemmed, '../data/dictionary_no_stemmed.json', 'without stem')
