# Digital text watermarking program for the German language
An easy to use program to embed a unique marking into a German text using Natural Language (NL) watermarking techniques and the open-source Natural Language Processing (NLP) library spaCy.
For more details about spaCy visit the [official website](https://spacy.io/).

## Requirements
- Python version: Python 3.8+
- SpaCy version: 2.2.4+

One way to install the latest version of spaCy and all dependencies is:
```
python -m venv .env
.env\Scripts\activate
pip install -U spacy
python -m spacy download de_core_news_sm
```
Further possibilities can be found at [Install spaCy](https://spacy.io/usage).

## Usage
The tool `WatermarkingProgram.py` can be executed using the command line.
To embed a specific marker in a text the following syntax is used:
```
python WatermarkingProgram.py -E <embed mode> <path to original file> <path to output file> <secret key> <text to embed> <watermarking methods>
```
   - **Embed mode:**			A blind <-B> and a non-blind <-N> mode is available.
   - **Path to original file:**	Specifies the absolute or relative path to the file to be marked.
   - **Path to output file:**	Defines the absolute or relative path including the filename to save the selected file.
   - **Secret key:**			This is the secret key, which can be freely defined. It may contain upper and lower case letters, numbers and special characters. This key must be kept secret, because the embedded watermark can be read using this key.
   **Text to embed:**		Represents the message to be embbed. It consists of a maximum of 30 characters and can contain numbers and letters of the German alphabet.
   **Watermarking methods:**	Any number of methods can be listed one after the other, separated by space.


The syntax to extract a marking is as follows:
```
python WatermarkingProgram.py -A <extraction mode> <path to marked file> <secret key> <path to original file>
```
   - **Extraction mode:**			A blind <-B> and a non-blind <-N> mode is available.
   - **Path to marked file:**		Specifies the absolute or relative path to the file to read a watermark from.
   - **Secret key:**				The secret key that was used for embedding.
   - **Path to original file:**	Specifies the absolute or relative path to the original unmarked file. However, this must only be specified when using the non-blind extraction mode <-N>.


**Currently only text files are supported!**
