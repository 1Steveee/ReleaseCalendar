from threading import Thread

import requests
from datetime import date
import time


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
                        # if product not already on release calendar, then alert and add to monitor list
                        if product['styleColor'] not in self.upcomingStock:
                            # if not active and release date is in the future, then alert discord and add to lists
                            if not product['isActive'] and product['releaseDate'] > today:
                                self.upcomingStock.append(product['styleColor'])
                                print(f'New product added to release calendar - {product["name"]}')
                        # if product is already on the release calendar and the date is in the past, then remove
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
