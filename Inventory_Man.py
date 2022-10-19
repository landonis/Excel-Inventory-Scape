import sys, json
from datetime import date

from scrape import parsing_session
from Sheet_man import Sheet_Man
from Inventory_obj import Inventory_Object
config_path='./config.json'
default_config_path = './default.json'

def build_config_file(path=config_path):
    d_str = None
    with open(default_config_path) as d:
        d_str = d.read()
    with open(path, 'w') as f:
        f.write(d_str)

class Inventory_Man: #interacts with other classes 
    def __init__(self, path_to_csv):
        self.path = path_to_csv
        self.sheet_man = None
        self.block_id = None
        self.config = self.load_config()
        self.items_to_update = self.get_outdated_blocks()
        if len(self.items_to_update)>0:
            for inv_obj in self.items_to_update:
                try:
                    if hasattr(inv_obj, 'href'):
                        self.run(inv_obj)
                    else:
                        print('failed because of no href value in inv_obj, check the column value in config file against where the href value is in excel')
                except RuntimeError as e:
                    print('failed to run object {} \n {}'.format(inv_obj, e))
        #self.update_file()

    def get_outdated_blocks(self):
        update_set = None
        self.sheet_man = Sheet_Man(self.path, self, self.config['excel-config'])
        for key in self.config['update']:
            if self.config['update'][key]['set']=='True':
                return self.sheet_man.get_list(self.config['update'][key])


    def build_inv_obj(self, href, row):
        domain_list = self.config['domain'].keys()
        for domain in domain_list:
            if href.find(domain)!=-1:
                return Inventory_Object(href, row, domain)

    def load_config(self):
        with open('./config.json', 'r') as config_file:
            return json.loads(config_file.read())

    def run(self, item):
        try:
            cur_date = date.today()
            session = parsing_session(item)
            
            data = session.find_data(**self.config['domain'][item.domain])
            data.update({'last_update': cur_date})
            print(data.keys())
            for key, it in data.items():
                print('key = {}  item = {}'.format(key, it))
                if hasattr(item, str(key)):
                    print('data obj has attribute {}, sending to excel'.format(key))
                    setattr(item, str(key), str(data[key]))            
                    self.sheet_man.update_block(item, key, str(data[key]))
        except RuntimeError as e:
            print('failed to run in run() for {} \n {}'.format(item, e))  
            
    def update_item(self, item):
        cur_date = date.today()
        print('creating connection for obj, date : {}'.format(cur_date))
        session = parsing_session(item)
        try:
            title, sku, price, available = session.Find_json_data()
        except:
            print("JSON data retrieval failed, trying backup options..")
            title, sku, price, available = 'failed', 'failed', 'failed', 'failed'
        if price=='failed':
            title = session.find_title()
            price = session.find_price()
            sku = session.find_sku()
            print('pass 2 price : {}'.format(price))
            print('pass 2 title : {}'.format(title))
            print('pass 2 sku : {}'.format(sku))

        
        setattr(item, 'last_updated', cur_date)
        self.sheet_man.update_block(item, self.block_id['last_update'], str(cur_date))
        setattr(item, 'title', title)
        self.sheet_man.update_block(item, self.block_id['title'], str(title))
        setattr(item, 'sku', sku)
        self.sheet_man.update_block(item, self.block_id['sku'], str(sku))
        setattr(item, 'price', price)
        self.sheet_man.update_block(item, self.block_id['price'], str(price))
        setattr(item, 'available', available)
        self.sheet_man.update_block(item, self.block_id['available'], str(available))

if __name__=="__main__":
    for arg in sys.argv:
        tag = arg.split('=',1)
        if tag[0]=='path':
            print('supplied excel path: ',tag[1])
            session = Inventory_Man(tag[1])
        elif tag[0]=='run':
            if tag[1]=='sheet':
                print('Generating a new sheet...')
            elif tag[1]=='config':
                print('Generating default config file')
                build_config_file()