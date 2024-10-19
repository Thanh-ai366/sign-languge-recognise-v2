from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sign-language-recogniser",  
    version="1.0.0", 
    author="Ta Phu Thanh",  
    author_email="taphuthanhtaphuthanh12345@gmail.com",  
    description="A Python package for sign language recognition using CNN models",
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    url="https://github.com/Thanh-ai366/sign-languge-recognise-v2",  
    packages=find_packages(),  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',  
    install_requires=[  
        "tensorflow>=2.0.0",
        "opencv-python",
        "numpy",
        "flask",
        "pyqt5",
        "fpdf",
        "sqlalchemy",
        "pyttsx3",
        "skimage",
        "matplotlib",
        "argparse", 
        "redis",
        "argon2-cffi"
    ],
    entry_points={  
        'console_scripts': [
            'sign-language-recogniser=app.main:main',
        ],
    },
    include_package_data=True,  
)
