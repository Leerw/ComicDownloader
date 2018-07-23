import scrapy
from scrapy.selector import Selector
import urllib.parse
from .chs2arabic import *
import re
from urllib import request
from urllib.request import urlopen
import os
from multiprocessing.dummy import Pool as ThreadPool

class ComicDownloader(scrapy.Spider):

    name = 'comic'
    start_urls = ['http://so.kukudm.com/']
    base_url = 'http://so.kukudm.com'
    page_url = 'http://comic.kukudm.com'
    download_dir = '/media/leerw/Entertainments/Comic/'

    CN_NUM = {
        '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '零': 0,
    }

    def parse(self, response):
        comicname = input("""please type the name of comic following volume (alternative) you want to download (eg. 火影忍者 or 火影忍者 第三卷)：\n""")

        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

        if -1 != comicname.find(' '):
            [comicname, volume] = comicname.split()
            self.comicname = comicname
            volume = volume[1:-1]
            volume = chinese_to_arabic(volume)
            self.volume = volume
        else:
            [comicname, volume] = [comicname, '']
            self.comicname = comicname
            self.volume = ''

        path = self.download_dir + comicname
        if not os.path.exists(path):
            os.mkdir(path)

        comicname = urllib.parse.quote(string=comicname, encoding='gb2312')

        searchasp = 'http://so.kukudm.com/search.asp?kw='
        searchurl = searchasp + comicname + '&Submit=%C8%B7%B6%A8'
        yield scrapy.Request(url=searchurl, callback=self.parse_comic_search)
        pass

    def parse_comic_search(self, response):
        comicurl = response.xpath('//dd/a/@href').extract_first()
        yield  scrapy.Request(url=comicurl, callback=self.parse_comic)

    def parse_comic(self, respone):
        volumes = {}
        dds = respone.xpath('//dl[@id="comiclistn"]/dd').extract()
        for dd in dds:
            sel = Selector(text=dd)
            href = self.page_url + sel.xpath('//a/@href').extract_first()
            text = sel.xpath('//a/text()').extract_first()
            volumes[text] = href

        if self.volume != '':
            # specified volume
            volname = str(self.volume)
            vollink = ''
            for key, value in volumes.items():
                find = re.findall(r"Vol_(.+?)$", key)
                if len(find) and find[0] == volname:
                    vollink = value
                    volname = key
                    break
            if vollink != '':
                # find it and download it
                self.save_volume(vollink, volname)
                pass
            pass
        else:
            for key, value in volumes.items():
                self.save_volume(value, key)
            pass

    def save_volume(self, vol_link, volname):
        base_img_url = 'http://n5.1whour.com/comic/'
        volname.strip()
        volpath = os.path.join(self.download_dir, self.comicname, volname)
        exists = os.path.exists(volpath)
        if not exists:
            os.mkdir(volpath)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        req = request.Request(url=vol_link, headers=headers)
        content = urlopen(req).read().decode('gbk')
        selector = Selector(text=content)
        image = selector.xpath('//body//table').extract()[1]
        total_page = int(re.findall(r"共(.+?)页", str(image))[0])
        digits = len(str(total_page))
        url = base_img_url + re.findall(r"comic/(.+?)JPG", str(image))[0] + 'jpg'

        img_urls = []
        paths = []

        for i in range(1, total_page):
            i = str(i).zfill(digits)
            url = url[:-4-digits] + i + url[-4:]
            path = os.path.join(volpath, i + '.jpg')

            img_urls.append(url)
            paths.append(path)

        pool = ThreadPool(100)
        pool.starmap(self.save_image, zip(img_urls, paths))

        pass

    def save_image(self, img_url, path):
        if os.path.exists(path):
            return
        try:
            request.urlretrieve(img_url, path)
            self.log('downloading...' + path)
        except:
            pass

