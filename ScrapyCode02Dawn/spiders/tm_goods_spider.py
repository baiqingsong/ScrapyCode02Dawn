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