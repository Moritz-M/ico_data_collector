import requests
import hmac
import hashlib
import datetime
import json
import base64
from pprint import pprint
import shutil
import os
from tqdm import tqdm

import csv

class ICObench:
    def __init__(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.privateKey = config['ICObench']['privateKey']
            self.publicKey = config['ICObench']['publicKey']
            self.apiUrl = config['ICObench']['apiUrl']

    def sendRequest(self, path='', data=()):
        hash = hmac.new(self.privateKey.encode('utf-8'), ''.encode('utf-8'), hashlib.sha384)
        dataJSON = json.dumps(data)
        hash.update(dataJSON.encode('utf-8'))
        sign = hash.digest()
        sign = base64.b64encode(sign)

        request_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-ICObench-Key': self.publicKey,
            'X-ICObench-Sig': sign
        }

        url = self.apiUrl + path;
        dataJSON = json.dumps(data)
        response = requests.post(url=url, data=dataJSON, headers=request_headers)
        return response

    # get the number of available pages 
    def get_available_pages(self):
        response =  self.sendRequest(path = "icos/all")
        return response.json()['pages']

    # get the number of available ICOs
    def get_available_icos(self):
        response =  self.sendRequest(path = "icos/all")
        return response.json()['icos']

    # get corresponding page given a page number
    def get_corresponding_page(self, page_number):
        response = self.sendRequest(path = 'icos/all', data = {'page':page_number })
        return response.json()

    # get all details about an ico given an id
    def get_ico_by_id(self, id):
        response = self.sendRequest(path = 'ico/'+str(id))
        return response.json()

    def get_all_ids(self):
        all_ids = []

        pages = self.get_available_pages()
        print('Collecting IDs from ', pages, ' pages. This might take a while.')
        for page in tqdm(range(pages+1)):  
            response = self.get_corresponding_page(page)

            if 'results' in response:
                for ico in response['results']:
                    all_ids.append(ico['id'])
                #print('getting ids from page', page+1, '/', pages, '\t ICO count: ', len(all_ids))

        print('\nscraped ',len(all_ids), 'ids from ', pages, ' pages\n')

        with open('id_list.txt', 'w') as f:
            for index, ico_id in enumerate(all_ids):
                f.write(str(ico_id)+ '\n')

    def add_ico_detail_to_csv(self, ico):
        with open('ICObench_icos.csv', 'a') as f:
            writer = csv.writer(f)
            row = []
            for entry in ico:
                line = str(ico[entry])
                line = line.replace('\n',' ')
                line = line.replace('\r','')
                line = line.replace('\t',' ')
                line = line.replace('<br />','')
                row.append(line)
            writer.writerow(row)

    def check_completeness(self):
        soll_id_list = []
        with open('id_list.txt', 'r') as f:
            soll_id_list = f.read().splitlines()

        ist_id_list = []
        with open('ICObench_icos.csv', 'r') as f:
            ico_list = csv.reader(f)
            for row in ico_list:
                ist_id_list.append(row[0])

        print('soll: ', len(soll_id_list), '     ist: ', len(ist_id_list)-1)

        if(len(soll_id_list) == len(ist_id_list)-1):
            print('\n\nIntegrity checked, all', len(ist_id_list),'icos scraped')
            output_json = {}
            with open('output_check.json', 'r') as f:
                output_json = json.load(f)
                output_json['ICObench']['status'] = 'complete'
            with open('output_check.json', 'w') as f:
                json.dump(output_json, f)

            os.remove('id_list.txt')
            os.remove('id_list_queue.txt')
            os.rename('ICObench_icos.csv', 'ICObench_icos_'+str(datetime.date.today())+'.csv')

        else:

            soll_set = set(soll_id_list)
            ist_set = set(ist_id_list)

            rest_set = soll_set - ist_set

            with open('id_list_queue.txt', 'w') as f:
                for e in rest_set:
                    f.write(str(e)+ '\n')

            self.get_icos_from_id_list()
            self.check_completeness()

    def get_icos_from_id_list(self):
        id_list = []

        with open('id_list_queue.txt', 'r') as f:
            id_list = f.read().splitlines()

        print('Now getting all ICOs and adding them to the csv file')
        for i in tqdm(range(len(id_list))):
            ico_id = id_list[0]
            #print(i+1, '- ', ico_id)

            ico_json = self.get_ico_by_id(ico_id)
            self.add_ico_detail_to_csv(ico_json)
            id_list.remove(ico_id)

            with open('id_list_queue.txt', 'w') as q:
                for _, ico_id in enumerate(id_list):
                    q.write(str(ico_id)+ '\n')

    def check_previous_completeness(self):
        with open('output_check.json', 'r') as f:
            output_check = json.load(f)
            output_check = output_check['ICObench']['status']
            if (output_check == 'unfinished'):
                return False
            else:
                return True

    def add_titles_to_csv(self):
        key_list = []
        with open('id_list.txt', 'r') as id_list_file:
            ico_id = id_list_file.read().splitlines()[0]
            ico_details = self.get_ico_by_id(ico_id)
            key_list = dict(ico_details).keys()

            with open('ICObench_icos.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(key_list)

    def change_status_to_unfinished(self):
        output = {}
        with open('output_check.json', 'r') as f:
            output = json.load(f)
        output['ICObench']['status'] = 'unfinished'
        
        with open('output_check.json', 'w') as f:
            json.dump(output, f)

    def setup_clean_files(self):
        if(not os.path.isdir('./archive')):
            os.makedirs('./archive')

        for file in os.listdir('.'):
            if (file.endswith('.csv')):
                shutil.move('./'+file, './archive/'+file)

        with open('./id_list.txt', 'w'):
            pass
        with open('./id_list_queue.txt', 'w'):
            pass
        with open('./ICObench_icos.csv', 'w'):
            pass

    def get_csv(self):
        if(self.check_previous_completeness()):
            print("\n\nPrevious run was complete. Starting a new search!\n")
            self.setup_clean_files()
            self.get_all_ids()
            shutil.copyfile('./id_list.txt', './id_list_queue.txt')
            self.change_status_to_unfinished()
            self.add_titles_to_csv()
            self.get_icos_from_id_list()
            self.check_completeness()
        else:
            print("\n\nPrevious run was NOT complete. Continuing last search! \nIf you do not wish to continue last search, change -status- in output_check.json to -complete-\n ")
            self.get_icos_from_id_list()
            self.check_completeness()

        
def main():
    ico_bench = ICObench()
    ico_bench.get_csv()

if __name__ == "__main__":
    main()
