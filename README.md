# Overview
Use Wikipedia API to read content from Wikipedia. Rather than call the API directly, we use third-party package `mwclient` for this purpose.

We start from a seed list of titles. These are typically outlines and indices that simply link to other articles. We crawl these and extract article titles from the links contained in seed content.

Once we've got article titles from the seed, we can crawl them. Full content of each article is stored. In addition, we parse each article to identify more articles to crawl.

Not all titles are relevant to our work. For example, we may be interested in only tech-related articles or we wish to discard biographies. We do filtering. To aid this process, we use a list of common English words. We may use [Mieliestronk's 58K wordlist](http://www.mieliestronk.com/wordlist.html) for this purpose. These are saved in `data/words.txt`.


# Installation
Run the following to install the pre-requisites:
```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

If you've problem installing `spacy` on Windows (perhaps due to C++ compiler issues), try Anaconda distribution and install it via Anaconda. This distribution may have a slightly older version of `spacy`.


# Usage
Before invoking the script, you may wish to check or alter values in the configuration file `config.json`. You can also modify the seed lists in folder `data/`.

File `main.py` is the entry point. Run `main.py -h` to view the various options. Typically, the following sequence of commands should suffice:
```
# Seed titles to crawl and save into folder week23
# Process a maximum of 200 titles
# This may be called multiple times until the seed list is exhausted
main.py -s -d week23 -m 200

# After seeding, crawl actual articles
# Use the default maximum of articles to crawl
# -r option: do restricted parsing of article content
main.py -r -d week23
```

To crawl continuously (Ctrl-C to terminate), do batch runs:
```
# Save files within the default path
sh runner.sh

# Save files within the specified path (example here is `week23`)
sh runner.sh week23
```

Output files are stored within path `output/` by default. However, this can be changed via `-b` option. For example, when running on Google Colab, you can change this to store files on your Google Drive space. Files with prefix `seed` may not be useful. Other files contain the actual content of articles.

If you already have a list of article titles to crawl, skip seeding. Save the article titles into the pending file. Delete crawled/discarded/redirected files. File names are as in `config.json`. Run the command `main.py -r -d {yourdir}`. Here's an example:
```
# Crawl a list of titles directly without any seeding
# Place the titles in file week23/pending_titles.txt, one title per line
# -l option: stop crawling at a specific level
main.py -d week23 -l 1
```


# Seeding

Seed files could be automatically created but since we're interested in only specific domains (such as Computer Science or Technology), this approach is not followed.

The seed file `data/seed-basic-tech.txt` was created manually from these sources:
* [Tech outlines](https://en.wikipedia.org/wiki/Wikipedia:Contents/Outlines#Technology_and_applied_sciences)
* [Outline of academic disciplines](https://en.wikipedia.org/wiki/Outline_of_academic_disciplines#Computer_Science)
* [Tech lists](https://en.wikipedia.org/wiki/Wikipedia:Contents/Lists#Technology_and_applied_sciences)
* [Tech indices](https://en.wikipedia.org/wiki/Wikipedia:Contents/Indices#Technology_and_applied_sciences)
* [Tech glossaries](https://en.wikipedia.org/wiki/Wikipedia:Contents/Technology_and_applied_sciences#Glossaries)
