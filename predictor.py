import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils import to_categorical

class Predictor:
    def __init__(self, abstracts, action):
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit_transform(abstracts)
        vectors = self.vectorizer.transform(abstracts)

        def rename(label):
            if label == 'include':
                return 0
            if label == 'exclude':
                return 1
            else:
                return 2
        labels = action.apply(rename)
        cat_labels = to_categorical(labels)

        self.model = Sequential()
        self.model.add(Dense(150, input_shape=(vectors.shape[1],), activation='relu'))
        self.model.add(Dense(150, activation='relu'))
        self.model.add(Dense(3, activation='softmax'))
        self.model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        self.model.fit(vectors[:len(cat_labels)], cat_labels, epochs=4, batch_size=10)

    def get_prediction(self, abstract):
        a = [abstract]
        vector = self.vectorizer.transform(a)
        prediction = self.model.predict(vector)[0]
        maxpred = max(prediction)
        print(prediction, maxpred)
        return [maxpred==pred for pred in prediction]
