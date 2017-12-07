# scrapy项目2--天猫商城

* (创建工程)[#创建工程]
* (item编写)[#item编写]
* (spider编写)[#spider编写]
* (settings设置)[#settings设置]
* (保存数据)[#保存数据]

## 创建工程
在命令行中当前文件夹下
```
scrapy startproject ScrapyCode02Dawn
```
运行创建功能命令

## item编写
```
class TopgoodsItem(scrapy.Item):
    GOODS_PRICE = scrapy.Field()
    GOODS_NAME = scrapy.Field()
    GOODS_URL = scrapy.Field()
    SHOP_NAME = scrapy.Field()
    SHOP_URL = scrapy.Field()
    COMPANY_NAME = scrapy.Field()
    COMPANY_ADDRESS = scrapy.Field()
    # 图片链接
    file_urls = scrapy.Field()
```

## spider编写
```
# _*_ coding:utf-8 _*_
import scrapy
from ScrapyCode02Dawn.items import TopgoodsItem

class TmGoodsSpider(scrapy.Spider):
    name = "tm_goods"
    allowed_domains = ["http://www.tmall.com"]
    start_urls = ["https://list.tmall.com/search_product.htm?q=%C5%AE%D7%B0&type=p&spm=a220m.1000858."
                  "a2227oh.d100&from=.list.pc_1_searchbutton"]

    # 记录处理的页数
    count = 0
    def parse(self, response):
        TmGoodsSpider.count += 1
        divs = response.xpath('//div[@id="J_ItemList"]/div[@class="product item-1111 "]/div[@class="product-iWrap"]')
        if not divs:
            self.log("List Page error--%s" % response.url)
        for div in divs:
            item = TopgoodsItem()
            item['GOODS_PRICE'] = div.xpath('p[@class="productPrice"]/em/@title')[0].extract()
            item['GOODS_NAME'] = div.xpath('p[@class="productTitle"]/a/@title')[0].extract()
            pre_goods_url = div.xpath('p[@class="productTitle"]/a/@href')[0].extract()
            item['GOODS_URL'] = pre_goods_url if "http:" in pre_goods_url else ("http:" + pre_goods_url)
            # 图片链接
            try:
                file_urls = div.xpath('div[@class="productImg-wrap"]/a[1]/img/@src|'
                                      'div[@class="productImg-wrap"]/a[1]/img/@data-ks-lazyload').extract()[0]
                item['file_urls'] = ["http:" + file_urls]
            except Exception,e:
                print "Error:",e
                # 方便代码调试
                # import pdb;pdb.set_trace()
            yield scrapy.Request(url=item['GOODS_URL'], meta={'item':item}, callback=self.parse_detail, dont_filter=True)

    def parse_detail(self, response):
        div = response.xpath('//div[@class="extend"]/ul')
        if not div:
            self.log("Detail Page error--%s" % response.url)
        item = response.meta['item']
        div = div[0]
        item['SHOP_NAME'] = div.xpath('li[1]/div/a/text()')[0].extract()
        item['SHOP_URL'] = div.xpath('li[1]/div/a/@href')[0].extract()
        item['COMPANY_NAME'] = div.xpath('li[3]/div/text()')[0].extract().strip()
        item['COMPANY_ADDRESS'] = div.xpath('li[4]/div/text()')[0].extract().strip()

        yield item
```

## settings设置
```
ITEM_PIPELINES = {'scrapy.pipelines.images.ImagesPipeline':1}
IMAGES_URLS_FIELD = "file_urls"
IMAGES_STORE = r'.'
# IMAGE_THUME = {
#     'small':(50, 50),
#     'big':(270, 270),
# }

LOG_FILE = "scrapy.log"
```

## 保存数据
命令行执行代码
```
scrapy crawl tm_goods -o result.csv
```
result.csv可以用excel表格打开  
如果result中出现乱码，则使用Notpad++打开，选择格式-转为ANSI编码格式-另存为  
然后使用excel打开，然后另存为得到要求的excel文件

注意保存图片需要在settings.py中设置，但是需要安装PIL。  
命令行安装
```
pip install pillow
```

注：遇到的问题
```
exceptions.ImportError:No module named PIL
```
是因为下载图片中没有安装pil引起的
```
ValueError('Missing scheme in request url: %s' % self._url)
```
是因为保存图片应为数组保存，将地址改成数组形式