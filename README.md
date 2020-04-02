# Overview
Use Wikipedia API to read content from Wikipedia. Rather than call the API directly, we use third-party package `mwclient` for this purpose. We start from a seed list of article titles. We crawl these articles via the API. Then we extract more article titles from the links contained in crawled articles. These new titles will be crawled at the next batch.

Not all titles are relevant to our work. For example, we may interested in only tech-related articles. Thus, the seed articles should be formed as such. In addition, we filter out titles that are not irrelevant. To aid this process, we use a list of common English words. We may use [Mieliestronk's 58K wordlist](http://www.mieliestronk.com/wordlist.html) for this purpose. These are save in `data/words.txt`.


# Installation
Run the following to install the pre-requisites:
```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

If you've problem installing `spacy` on Windows (perhaps due to C++ compiler issues), try Anaconda distribution and install it via Anaconda. This distribution may have a slightly older version of `spacy`.

# Usage
Before invoking the script, you may wish to check or alter values in the configuration file `config.json`. You can also modify the seed list in `data/seed_titles.txt`.

File `main.py` is the entry point. Here are some useful commands:
* `main.py`: start with seed titles
* `main.py -c`: continue with pending titles identified from earlier crawls
* `main.py -r`: restricted crawl so that only relevant articles are obtained
* `main.py -h`: show help

Output files are stored within path `output/` by default. However, this can be configured in `config.json`. For example, when running on Google Colab, you can change this to store files on your Google Drive space.

To crawl continuously (Ctrl-C to terminate), do batch run:
* `sh runner.sh`: files are saved within default path
* `sh runner.sh friday_runs`: files are saved in the specified path (example here is `friday_runs`)
