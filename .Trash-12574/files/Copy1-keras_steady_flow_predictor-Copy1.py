'''Trains a simple convnet on the MNIST dataset.

Gets to 99.25% test accuracy after 12 epochs
(there is still a lot of margin for parameter tuning).
16 seconds per epoch on a GRID K520 GPU.
'''

# keras import stuff
import matplotlib.pyplot as plt
import numpy as np
import vtk
import os
import keras
from keras.models import Model
from keras.layers import (
    Input, 
    concatenate, 
    Conv2D, 
    MaxPooling2D, 
    Conv2DTranspose,
    ZeroPadding2D  # Move this here instead of importing from convolutional
)
from keras import backend as K
import vtk
import tensorflow as tf

# vtm dataset maker
from vtm_data import VTK_data

# numpy and matplot lib


# training params
batch_size = 32
epochs = 100 # number of times through training set

# load dataset
#dataset = VTK_data("../data")
#dataset.load_data()

from pathlib import Path

class VTK_data:
    def __init__(self, base_path, split_ratio=0.8):
        self.base_path = Path(base_path)
        self.data = []
        self.geometries = []
        self.steady_flows = []
        self.split_ratio = split_ratio
        self.split_line = 0
        
    def load_data(self):
        for dirpath, dirnames, filenames in os.walk(self.base_path):
            for filename in filenames:
                if filename.endswith('.vtm'):
                    full_path = Path(dirpath) / filename
                    try:
                        data = self._load_single_file(full_path)
                        if data is not None:
                            print(f"\nProcessing file: {filename}")
                            print(f"Full path: {full_path}")
                            
                            # Updated classification logic
                            if 'geometry' in filename:
                                print(f"Classified as geometry file")
                                self.geometries.append(data)
                            elif 'cylinder2d_iT' in filename:
                                print(f"Classified as flow file")
                                self.steady_flows.append(data)
                            else:
                                print(f"Skipping file: {filename}")
                    except Exception as e:
                        print(f"Error loading {full_path}: {str(e)}")
        
        print("\nLoaded data summary:")
        print(f"Number of geometry files: {len(self.geometries)}")
        if self.geometries:
            print(f"Shape of first geometry: {np.array(self.geometries[0]).shape}")
        
        print(f"Number of flow files: {len(self.steady_flows)}")
        if self.steady_flows:
            print(f"Shape of first flow: {np.array(self.steady_flows[0]).shape}")
        
        total_samples = len(self.geometries)
        self.split_line = int(total_samples * self.split_ratio)
        
        return self.geometries, self.steady_flows
    
    def _load_single_file(self, file_path):
        reader = vtk.vtkXMLMultiBlockDataReader()
        reader.SetFileName(str(file_path))
        reader.Update()
        
        if reader.GetErrorCode() != 0:
            raise RuntimeError(f"Error reading file")
        
        data = reader.GetOutput()
        if data is None:
            raise RuntimeError("No data read from file")
            
        data_iterator = data.NewIterator()
        img_data = data_iterator.GetCurrentDataObject()
        
        if img_data is None:
            raise RuntimeError("No image data found in file")
        
        if hasattr(img_data, 'GetProducerPort'):
            producer = img_data.GetProducerPort()
            if producer:
                producer.Update()
        elif hasattr(img_data, 'GetSource'):
            source = img_data.GetSource()
            if source:
                source.Update()
                
        point_data = img_data.GetPointData()
        array_data = point_data.GetArray(0)
        array_data = vtk.util.numpy_support.vtk_to_numpy(array_data)
        
        return array_data

# Create instance and load data
base_directory = "../data"
dataset = VTK_data(base_directory)

# Load the data
geometries, steady_flows = dataset.load_data()

if len(dataset.geometries) > 0 and len(dataset.steady_flows) > 0:
    # Get train and test split
    train_geometries = dataset.geometries[0:dataset.split_line]
    train_steady_flows = dataset.steady_flows[0:dataset.split_line]
    test_geometries = dataset.geometries[dataset.split_line:-1]
    test_steady_flows = dataset.steady_flows[dataset.split_line:-1]
    
    print("\nData split sizes:")
    print(f"Train geometries: {len(train_geometries)}")
    print(f"Train flows: {len(train_steady_flows)}")
    print(f"Test geometries: {len(test_geometries)}")
    print(f"Test flows: {len(test_steady_flows)}")
    
    # Convert to numpy arrays
    train_geometries = np.stack(train_geometries, axis=0)
    train_steady_flows = np.stack(train_steady_flows, axis=0)
    test_geometries = np.stack(test_geometries, axis=0)
    test_steady_flows = np.stack(test_steady_flows, axis=0)
    
    print("\nFinal array shapes:")
    print(f"Train geometries shape: {train_geometries.shape}")
    print(f"Train flows shape: {train_steady_flows.shape}")
    print(f"Test geometries shape: {test_geometries.shape}")
    print(f"Test flows shape: {test_steady_flows.shape}")
else:
    print("\nERROR: Missing either geometry or flow data!")


# get train and test split
train_geometries = dataset.geometries[0:dataset.split_line]
train_steady_flows = dataset.steady_flows[0:dataset.split_line]
test_geometries = dataset.geometries[dataset.split_line:-1]
test_steady_flows = dataset.steady_flows[dataset.split_line:-1]

print(f"Training set size: {len(train_geometries)} samples")
print(f"Test set size: {len(test_geometries)} samples")

# reshape into single np array
train_geometries = np.stack(train_geometries, axis=0)
train_steady_flows = np.stack(train_steady_flows, axis=0)
test_geometries = np.stack(test_geometries, axis=0)
test_steady_flows = np.stack(test_steady_flows, axis=0)

# print dataset values
print('geometry shape:', train_geometries.shape[1:])
print('steady flow shape:', train_steady_flows.shape[1:])
print(train_geometries.shape[0], ' train samples')
print(test_geometries.shape[0], ' test samples')

# construct model
inputs = Input(train_geometries.shape[1:])




print(f"BREAK")









# 2 3x3 convolutions followed by a max pool
#conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
#conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
#pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)

# Force TensorFlow to use CPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from keras.layers import Input, Conv2D, MaxPooling2D, Reshape

# Configure TensorFlow to use CPU
tf.config.set_visible_devices([], 'GPU')

# First, let's calculate suitable dimensions for reshaping
def find_factors(n):
    sqrt_n = int(np.sqrt(n))
    while n % sqrt_n != 0:
        sqrt_n -= 1
    return sqrt_n, n // sqrt_n

height, width = find_factors(9812)
print(f"Reshaping to dimensions: {height} x {width}")

# Create the input layer with original shape
inputs = Input(shape=(9812,))

# Reshape the input to 4D format
reshaped = Reshape((height, width, 1))(inputs)

# Apply Conv2D layers
conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(reshaped)
conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv1)
pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)



























# 2 3x3 convolutions followed by a max pool
conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1)
conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv2)
pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)

# 2 3x3 convolutions followed by a max pool
conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(pool2)
conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv3)
pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)

# 2 3x3 convolutions followed by a max pool
conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(pool3)
conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv4)
pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)

# 2 3x3 convolutions
conv5 = Conv2D(512, (3, 3), activation='relu', padding='same')(pool4)
conv5 = Conv2D(512, (3, 3), activation='relu', padding='same')(conv5)

# 1 3x3 transpose convolution and concate conv4 on the depth dim
up6 = concatenate([ZeroPadding2D(((1,0),(1,0)))(Conv2DTranspose(256, (2, 2), strides=(2, 2), padding='same')(conv5)), conv4], axis=3)

# 2 3x3 convolutions
conv6 = Conv2D(256, (3, 3), activation='relu', padding='same')(up6)
conv6 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv6)

# 1 3x3 transpose convolution and concate conv3 on the depth dim
up7 = concatenate([ZeroPadding2D(((1,0),(1,0)))(Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(conv6)), conv3], axis=3)

# 2 3x3 convolutions
conv7 = Conv2D(128, (3, 3), activation='relu', padding='same')(up7)
conv7 = Conv2D(128, (3, 3), activation='relu', padding='same')(conv7)

# 1 3x3 transpose convolution and concate conv3 on the depth dim
up8 = concatenate([ZeroPadding2D(((0,0),(1,0)))(Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(conv7)), conv2], axis=3)

# 2 3x3 convolutions
conv8 = Conv2D(64, (3, 3), activation='relu', padding='same')(up8)
conv8 = Conv2D(64, (3, 3), activation='relu', padding='same')(conv8)

# 1 3x3 transpose convolution and concate conv3 on the depth dim
up9 = concatenate([ZeroPadding2D(((0,0),(1,0)))(Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(conv8)), conv1], axis=3)

# 2 3x3 convolutions
conv9 = Conv2D(32, (3, 3), activation='relu', padding='same')(up9)
conv9 = Conv2D(32, (3, 3), activation='relu', padding='same')(conv9)

# final 1x1 convolutions to get to the correct depth dim (3 for 2 xy vel and 1 for pressure)
conv10 = Conv2D(3, (1, 1), activation='linear')(conv9)

# construct model
model = Model(inputs=[inputs], outputs=[conv10])

# compile the model with loss and optimizer
model.compile(loss=keras.losses.mean_squared_error,
              optimizer=keras.optimizers.Adam(lr=1e-4),
              metrics=['MSE'])

# train model
model.fit(train_geometries, train_steady_flows,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_data=(test_geometries, test_steady_flows))

# evaluate on test set
score = model.evaluate(test_geometries, test_steady_flows, verbose=0)
print('Average Mean Squared Error:', score[0])

# display predictions on test set
predicted_steady_flow = model.predict(test_geometries, batch_size=batch_size)
for i in xrange(predicted_steady_flow.shape[0]):
  # plot predicted vs true flow
  velocity_image = np.concatenate([predicted_steady_flow[i,:,:,0], test_steady_flows[i,:,:,0], test_geometries[i,:,:,0]/10.0], axis=1)
  plt.imshow(velocity_image)
  plt.show()
  # plot predicted vs true pressure
  velocity_image = np.concatenate([predicted_steady_flow[i,:,:,2], test_steady_flows[i,:,:,2], test_geometries[i,:,:,0]/10.0], axis=1)
  plt.imshow(velocity_image)
  plt.show()
 



