import matplotlib.pyplot as plt
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


def heap_plot():
    pass


if __name__ == '__main__':
    zipf_plot('../data/dictionary_with_stopwords.json', '../data/dictionary.json')
