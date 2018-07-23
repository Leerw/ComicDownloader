# ComicDownloader

## Installation

```sh
git clone https://github.com/Leerw/ComicDownloader.git
conda env create -f enviroment.yml
```

## Specify your download directory

```
In ComicDownloader/spiders/ComicDownloader.py:line17
you can change the directory to save comic
eg.
    download_dir = 'your comic folder'
```

## Using

```sh
cd ComicDownloader
scrapy crawl comic

# input what you want to download (comicname) or (comicname volume)
please type the name of comic following volume (alternative) you want to download (eg. 火影忍者 or 火影忍者 第三卷)
```