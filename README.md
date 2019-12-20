# Medicinal-Search-Engine
Information Retrieval Course Project

##Requirements
- Mongo server ([Download](https://www.mongodb.com/download-center/community "Download"))
- Python (recommended v3.6)
- Git

## Installation
- Clone this repository in your preferred directory
`git clone https://github.com/prat-bphc52/Medicinal-Search-Engine.git`
- Install nltk using pip
`pip3 install nltk`
- Download the required packages using nltk
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
exit()
```
- Start mongoDB server where your database resides.
- Execute "index_generator.py" to create inverted index. The indexes will be stored in pickle files.
`py index_generator.py`
- To query results for any disease or symptoms, execute the python script 'Search_Query.py'
`py Search_Query.py`


# Team:
- Prateek Agarwal
- Shriya Choudhary
- Shreeya Nelekar
- Shubham Singhal