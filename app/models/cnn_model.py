import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Tạo Data Augmentation để tăng cường dữ liệu đầu vào
def create_data_generator():
    datagen = ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    return datagen

# Tạo mô hình CNN với các lớp Convolutional, Pooling, và Batch Normalization
def create_cnn_model(input_shape=(64, 64, 1), num_classes=36):
    model = Sequential()
    
    model.add(Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

    return model

# Tạo callback cho Early Stopping và Learning Rate Scheduler
def create_callbacks():
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3)
    return [early_stopping, lr_scheduler]

# Ví dụ sử dụng mô hình và data generator
if __name__ == "__main__":
    input_shape = (64, 64, 1)
    num_classes = 36
    
    # Tạo generator để augment dữ liệu huấn luyện
    data_generator = create_data_generator()

    # Tạo mô hình CNN
    model = create_cnn_model(input_shape, num_classes)

    # Tạo các callback (EarlyStopping, ReduceLROnPlateau)
    callbacks = create_callbacks()

    # Huấn luyện mô hình với dữ liệu được tăng cường
    model.fit(
        data_generator.flow(train_images, train_labels, batch_size=32),
        validation_data=(validation_images, validation_labels),
        epochs=50,
        callbacks=callbacks
    )
