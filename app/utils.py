import os
import cv2

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def preprocess_image(image_path, size=(64, 64)):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, size)
    image = image / 255.0
    return image
