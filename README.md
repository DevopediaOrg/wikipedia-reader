# Overview
Use Wikipedia API to read content from Wikipedia. Rather than call the API directly, we use third-party package `mwclient` for this purpose. We start from a seed list of article titles. We crawl these articles via the API. Then we extract more article titles from the links contained in crawled articles. These new titles will be crawled at the next batch.

Not all titles are relevant to our work. For example, we may interested in only tech-related articles. Thus, the seed articles should be formed as such. In addition, we filter out titles that are not irrelevant. To aid this process, we use a list of common English words. We may use [Mieliestronk's 58K wordlist](http://www.mieliestronk.com/wordlist.html) for this purpose. These are save in `data/words.txt`.


# Usage
Before invoking the script, you may wish to check or alter values in the configuration file `config.json`. You can also modify the seed list in `data/seed_titles.txt`. You can need to download a spaCy model:
```
python -m spacy download en_core_web_sm
```

File `main.py` is the entry point. Here are some useful commands:
* `main.py`: start with seed files
* `main.py -p`: start with pending titles identified from earlier crawls
* `main.py -h`: show help

Output files are stored in folder `data/`.