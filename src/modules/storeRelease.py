from threading import Thread

import requests
from datetime import date
import time
from discord_webhook import DiscordWebhook, DiscordEmbed


class StoreRelease:
    def __init__(self, site: str, url: str):
        self.site = site
        self.url = url
        self.upcomingStock = []
        self.cachestock()

    def monitor(self):
        """
        Method is responsible for parsing JSON object and comparing it to the current stock list
        :return:
        """
        while True:
            try:
                statusCode, jsonObj = self.getstock()

                today = date.today().strftime("%m/%d/%y")
                if statusCode:
                    for product in jsonObj['products']:
                        if product['styleColor'] not in self.upcomingStock:
                            if not product['isActive'] and product['releaseDate'] > today:
                                self.upcomingStock.append(product['styleColor'])
                                print(f'New product added to release calendar - {product["name"]}')
                        else:
                            if product['isActive'] and today > product['releaseDate']:
                                self.upcomingStock.remove(product['styleColor'])
                                print(f'Removed product from release calendar {product["name"]}')
                else:
                    print('Request failed to get future stock products, retrying')
            except Exception as e:
                print(f'An error occured trying to monitor stock, error {e}')

    def cachestock(self):
        """
        Method is responsible for storing a copy of the current future stock into a list
        List will be used to compare agaisnt future monitor runs
        While True runs until we get a successfull request
        :return: n/a
        """
        while True:
            try:
                statusCode, jsonObj = self.getstock()

                today = date.today().strftime("%m/%d/%y")
                if statusCode:
                    for product in jsonObj['products']:
                        if not product['isActive'] and product['releaseDate'] > today:
                            self.upcomingStock.append(product['styleColor'])
                            # embed = DiscordEmbed(title="New Product Added!", description="Lesss Cook", color='00FF00')
                            # embed.set_author(name="Vasilis Software")
                            # embed.set_footer(text=f"{self.site} Release Calendar")
                            # # Set `inline=False` for the embed field to occupy the whole line
                            # embed.set_thumbnail(url="https://dynl.mktgcdn.com/p/9mc68tD1fQAi5AZw6QOH8nW3U_YQ7Jg0UWvrDmXd5fI/1008x1008.png")
                            # embed.add_embed_field(name="Name", value=f"{product['name']}", inline=False)
                            # embed.add_embed_field(name="Release Date", value=f"{product['releaseDate']}", inline=False)
                            # embed.add_embed_field(name="Price", value=f"{product['salePrice']}")
                            # # embed.add_embed_field(name="Action",
                            # #                       value=f"[Product Page](https://www.finishline.com/store/product/fnl/prodclea{product['PRODUCT_ID']}?styleId={product['STYLE_ID']}&colorId={product['COLOR_ID']})")
                            # webhook = DiscordWebhook(
                            #     url='https://discord.com/api/webhooks/1016186649077633055/5Kwlelmi2-wAf9dX928QYe9dLE5akn13eR2eCGuVPXGmCk3VISJeFSikDyKj_6I29x_u',
                            #     rate_limit_retry=True)
                            # webhook.add_embed(embed)
                            # webhook.execute()
                    print(f'Cached all future release products, {self.upcomingStock}')
                    break
                else:
                    print('Request failed to get future stock products, retrying')
            except Exception as e:
                print(f'An error occured trying to cache stock, error {e}')

    def getstock(self):
        """
        Method is responsible for request
        Method gets upcoming release products
        :return: Returns httpStatus of True and json object if request was successful
        if request fails, it will return HttpStatus of False, and none
        """
        try:
            time.sleep(10)
            headers = {
                'authority': 'www.finishline.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.9',
                'referer': 'https://www.finishline.com/store/sneaker-release-dates?brand=jordan&ranMID=37731&ranEAID'
                           '=TnL5HPStwNw&ranSiteID=TnL5HPStwNw-KaJA4xRDBDff05Pa06JGtw&CMP=AFL-LS-affiliatechannel'
                           '&sourceid=affiliate&siteID=TnL5HPStwNw-KaJA4xRDBDff05Pa06JGtw&gclid'
                           '=CjwKCAjwv4SaBhBPEiwA9YzZvEZQA1Fcc31RwlnM61Wlq94nCNzBYfmSDP2Qq'
                           '-gsqDwAzHMXOLW2hxoCHD0QAvD_BwE&gclsrc=aw.ds',
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/105.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }

            url = self.url
            response = requests.get(url, headers=headers)

            print(f'Sent request to {url}, HTTP response status code {response.status_code}')
            if response.status_code == 200:
                return True, response.json()
            return False, None
        except Exception as e:
            print(f'Error occurred while getting upcoming stock, request failed {e}, retrying to get stock')


def thread_func():
    threads = []
    stores = [
        {
            'StoreName': 'Finishline',
            'url': 'https://www.finishline.com/store/releaseproduct/gadgets/releaseCalendarLookupAPI.jsp'
        },
        {
            'StoreName': 'JD Sports',
            'url': 'https://www.jdsports.com/store/releaseproduct/gadgets/releaseCalendarLookupAPI.jsp'
        }
    ]

    for store in stores:
        storeObj = StoreRelease(store['StoreName'], store['url'])
        threads.append(Thread(target=storeObj.monitor))

    for thread in threads:
        thread.start()


thread_func()
