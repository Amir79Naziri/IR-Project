from SearchEngine.preprocess import Preprocess
from SearchEngine.indexConstruction import PositionalIndex
from SearchEngine.queryProcessor import main

if __name__ == '__main__':
    preprocessor = Preprocess()
    preprocessor.start('./data/IR_data_news_12k.json', './data/main_data.json')

    positionalIndex = PositionalIndex()
    positionalIndex.create('./data/main_data.json', './data/dictionary.json')

    main('./data/dictionary.json', './data/IR_data_news_12k.json')
