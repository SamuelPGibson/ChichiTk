from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as file:
    long_description = "\n" + file.read()

VERSION = '0.0.1'
DESCRIPTION = 'Python UI library built upon Tkinter'
LONG_DESCRIPTION = 'Python UI library built upon Tkiner, which implements affectedly elegant extensions of existing tkinter widgets.'

# Setting up
setup(
    name="chichitk",
    version=VERSION,
    author="Samuel Gibson",
    author_email="<samuelpgibson12@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['opencv-python', 'numpy', 'Pillow', 'fitz'],
    keywords=['python', 'tkinter', 'custom', 'widgets'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)