import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils import to_categorical

class Predictor:
    def __init__(self, abstracts, action, num_actions=3):
        self.num_actions = num_actions
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit_transform(abstracts)
        vector_length = len(self.vectorizer.get_feature_names())


        self.model = Sequential()
        self.model.add(Dense(150, input_shape=(vector_length,), activation='relu'))
        self.model.add(Dense(50, activation='relu'))
        self.model.add(Dense(3, activation='softmax'))
        self.model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        self.train(abstracts, action)


    def train(self, abstracts, labels):
        vectors = self.vectorizer.transform(abstracts)

        labels = labels.apply(Predictor.rename)
        cat_labels = to_categorical(labels, num_classes=self.num_actions)

        self.model.fit(vectors[:len(cat_labels)], cat_labels, epochs=4, batch_size=10)


    def rename(label):
        if label == 'include':
            return 0
        if label == 'exclude':
            return 1
        else:
            return 2

    def update_predictor(self, abstract, label):
        abstracts = pd.Series([abstract])
        labels = pd.Series([label])
        self.train(abstracts, labels)

    def get_prediction(self, abstract):
        a = [abstract]
        vector = self.vectorizer.transform(a)
        prediction = self.model.predict(vector)[0]
        maxpred = max(prediction)
        print(prediction, maxpred)
        return prediction, [maxpred==pred for pred in prediction]
