from setuptools import setup, find_packages

setup(
    name="SignLanguageRecognition",
    version="1.1.0",
    description="Phần mềm nhận diện ngôn ngữ ký hiệu ",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python",
        "tensorflow",
        "scikit-learn",
        "speechrecognition",
        "pyaudio",
        "tkinter"
    ],
    entry_points={
        'console_scripts': [
            'sign-language-recognition=app.main:create_main_window'
        ]
    },
    include_package_data=True,
    package_data={
        'gui': ['assets/*']
    }
)
