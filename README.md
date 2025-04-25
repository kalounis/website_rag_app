# RAG APP FOR WEBSITE

This repository contains the backend code for a RAG-based web application designed to help customers find answers to questions they are struggling to find on the website's help page. The project is divided into three main steps to build the RAG:
- Help Page Web Scraping: Extract relevant information from the help page.
- Database Generation: Create the necessary database to store the extracted information.
- App Construction: Build the application that utilizes the database to provide answers.
The functions needed throughout the code have been implemented as modules, allowing them to be reused in other projects or for different purposes.

## Repository structure
```
├── requirements.txt                       # Dependencies
├── setup.sh                               # Deployment install script
└── src                                    # Source code
    ├── functions_api                      # Main functions
    │   ├── app_faiss.py                   # App code
    │   ├── generate_datastore_faiss.py    # Generate database
    │   └── webscrapping.py                # Webscrapping
    └── modules                            # Shared library code
        └── data                           # Data processing module
        └── rag                            # RAG Pipeline module
        └── web                            # Webscrapping module               
```
## Code description

### `setup.sh`
This script automates the installation and deployment process of specific components of the project.

### `requirements.txt`
List of Python dependencies required for the project. You can install these dependencies by running `pip install -r requirements.txt`.

### `src/`
This directory contains the source code of the project.
- **`functions_api/`**: Contains the code of the core functions.
  - **`app_faiss.py`**: Main code of the application.
  - **`generate_datastore_faiss.py`**: Build the chunks and setup the embeddings.
  - **`webscrapping.py`**: Scrapes the data of the website.
- **`modules/`**: Contains the shared library code used by the Lambda functions.
  - **`data`**: Shared functions used by `generate_datastore_faiss.py` to process the data scrapped.
  - **`rag`**: Shared functions used implementing the RAG Pipeline.
  - **`web`**: Shared functions used to scrap the data and put into shape the application.