import requests
import json
import csv
import datetime
from pprint import pprint

class CoinMarketCap:
    def __init__(self):
        with open('./config.json', 'r') as f:
            config = json.load(f)
            self.privateKey = config['CoinMarketCap']['privateKey']
            self.apiUrl = config['CoinMarketCap']['apiUrl']
            self.max_requests = config['CoinMarketCap']['max_requests']

    def send_request(self, path='', params={}):
        request_headers = {
            'X-CMC_PRO_API_KEY' : self.privateKey
        }
        url = self.apiUrl + path
        
        response = requests.get(url = url, params = params, headers = request_headers).json()
        if(response['status']['error_code'] != 0):
            print("Error in sending or receiving request. Error Code ", response['status']['error_code'])
            return {}
        
        return response['data']
        

    def save_coin_to_file(self, data):
        row = []
        row.append(data['name'])
        row.append(data['id'])
        row.append(data['slug'])
        row.append(data['symbol'])
        row.append(data['total_supply'])
        row.append(data['num_market_pairs'])
        row.append(data['max_supply'])
        row.append(data['cmc_rank'])
        row.append(data['circulating_supply'])
        row.append(data['date_added'])
        
        row.append(data['quote']['EUR']['price'])
        row.append(data['quote']['EUR']['volume_24h'])
        row.append(data['quote']['EUR']['percent_change_1h'])
        row.append(data['quote']['EUR']['percent_change_24h'])
        row.append(data['quote']['EUR']['percent_change_7d'])
        row.append(data['quote']['EUR']['market_cap'])
        row.append(data['quote']['EUR']['last_updated'])

        with open('CoinMarketCap.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def add_titles_to_csv(self):
        key_list = []
        key_list.append('name')
        key_list.append('id')
        key_list.append('slug')
        key_list.append('symbol')
        key_list.append('total_supply')
        key_list.append('num_market_pairs')
        key_list.append('max_supply')
        key_list.append('cmc_rank')
        key_list.append('circulating_supply')
        key_list.append('date_added')
        key_list.append('price')
        key_list.append('volume_24h')
        key_list.append('percent_change_1h')
        key_list.append('percent_change_24h')
        key_list.append('percent_change_7d')
        key_list.append('market_cap')
        key_list.append('last_updated')
        with open('CoinMarketCap.csv', 'w') as f:
            writer = csv.writer(f)
            f.write('\n\ntimestamp : '+str(datetime.date.today())+'\n\n\n\n')
            writer.writerow(key_list)
        
    def get_and_write_all_coins(self):
        data = self.send_request(path='cryptocurrency/listings/latest', params={
        'start': 1,
        'limit': self.max_requests,
        'convert': 'EUR'
        })
        self.add_titles_to_csv()
        for item in data:
            self.save_coin_to_file(item)
        
def main():
    cmc = CoinMarketCap()
    cmc.get_and_write_all_coins()

if __name__ == '__main__':
    main()