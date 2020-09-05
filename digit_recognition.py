# LOAD LIBRARIES
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D, BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import LearningRateScheduler
from PIL import Image
import PIL.ImageOps 
import matplotlib.pyplot as plt
import cv2

# LOAD THE DATA


# BUILD CONVOLUTIONAL NEURAL NETWORKS
class digit_recognizer (): 
    def __init__(self):
        self.nets = 7
        self.model = [0] * self.nets
        for j in range(self.nets):
            print(j)
            self.model[j] = Sequential()

            self.model[j].add(Conv2D(32, kernel_size = 3, activation='relu', input_shape = (28, 28, 1)))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Conv2D(32, kernel_size = 3, activation='relu'))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Conv2D(32, kernel_size = 5, strides=2, padding='same', activation='relu'))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Dropout(0.4))

            self.model[j].add(Conv2D(64, kernel_size = 3, activation='relu'))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Conv2D(64, kernel_size = 3, activation='relu'))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Conv2D(64, kernel_size = 5, strides=2, padding='same', activation='relu'))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Dropout(0.4))

            self.model[j].add(Conv2D(128, kernel_size = 4, activation='relu'))
            self.model[j].add(BatchNormalization())
            self.model[j].add(Flatten())
            self.model[j].add(Dropout(0.4))
            self.model[j].add(Dense(10, activation='softmax'))

            # COMPILE WITH ADAM OPTIMIZER AND CROSS ENTROPY COST
            self.model[j].compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
            self.model[j].load_weights("models/model" + str(j) + ".h5")

    def predict_by_pil(self, img_pil, show = False):
        return self.__predict(img_pil, show)

    def predict_by_path(self, img_path, show = False):
        img_pil = Image.open(str(i) + ".jpg")
        return self.__predict(img_pil, show)

    def __predict (self, img_pil, show = False):
        img_pil = PIL.ImageOps.invert(img_pil)
        img_data = img_pil.getdata()
        img_as_list = np.asarray(img_data, dtype=float) / 255
        img_as_list = img_as_list[:,[0]]

        img_as_list = img_as_list.reshape(img_pil.size)
        X_test = pd.DataFrame(img_as_list)
        X_test = X_test.values.reshape(-1,28,28,1)

        results = np.zeros( (X_test.shape[0],10) ) 
        for j in range(self.nets):
            results = results + self.model[j].predict(X_test)

        results = [i * 100 for i in results[0]]
        results = [list(map(int, results))]
        #print(results)

        #print(str(results))
        res = np.argmax(results,axis = 1)


        if (results[0][1] > 80):
            results = [1]
        else:
            results = np.argmax(results,axis = 1)

        if (show):
            results = pd.Series(results,name="Label")
            plt.figure(figsize=(15,6))
            for i in range(1):  
                plt.subplot(4, 10, i+1)
                plt.imshow(X_test[i].reshape((28,28)),cmap=plt.cm.binary)
                plt.title("predict=%d" % results[i],y=0.9)
                plt.axis('off')
            plt.subplots_adjust(wspace=0.3, hspace=-0.1)
            plt.show()
        #print(results[0])
        return str(results[0])

#recognizer = digit_recognizer()
#for i in range(45):
#    recognizer.predict_by_path(str(i) + ".jpg", True)