from datetime import date
from types import NoneType
import requests, sys, getopt, json
from bs4 import BeautifulSoup
from functools import reduce

from Inventory_obj import Inventory_Object
from Sheet_man import Sheet_Man
keywords = {'d':'domain','f':'find', 'fa':'find_all', 'rm':'remove', 'p':'pass'}

#TO-DO

def return_dict_path(d, *paths):
    result = []
    print(d)
    for key, value in d.items():
        ext = []
        for trail in paths:
            ext.append(trail)
        if isinstance(value, str):
            print(result)
            path = []
            path.extend(ext)
            path.append(key)
            path.append(value)
            result.append(path)
        elif isinstance(value,dict):
            next_path = return_dict_path(value, *ext+[key])
            result.extend(next_path)
        elif isinstance(value,list):
            p = []
            p.extend(ext)
            p.append(key)
            print(p)
            for i in value:
                print(i)
                var = p + [i]
                print(var)
                result.append(var)
    print('results: {}'.format(result))
    return result

class parsing_session:
    def __init__(self, inv_obj):
        try:
            self.returned_dict = {}
            if hasattr(inv_obj, 'href'):
                print('starting parsing session for obj {}'.format(getattr(inv_obj, 'href')))
                r = requests.get(getattr(inv_obj, 'href'))
                self.soup = BeautifulSoup(r.content, 'html.parser')
            else:
                print('failed for obj {}'.format(inv_obj))
        except RuntimeError as e:
            print('failed starting connection in parsing_session \n {}'.format(e))
    def get_json(self, value):
        return_data = {}
        high_pass = self.soup.find(value['find'][0], class_=value['find'][1])
        low_pass = high_pass.find_all(value['find_all'][0], type=value['find_all'][1])
        #print('LOWPASS\n\n\n{}'.format(low_pass))
        if len(low_pass)<1:
            return 'failed'
        for obj in range(len(low_pass)):
            
            newstr = low_pass[obj].text[low_pass[obj].text.find('{')-1:low_pass[obj].text.rfind('}')+1]
            data = json.loads(newstr)
            #paths = self.return_dict_path(value['named_objs'])
            print(data)
            for key in value['named_objs']:
                print(key)
                if isinstance(key, dict):
                    key_path = return_dict_path(key)
                    print('keypath*******{}'.format(key_path))
                    for paths in key_path:
                        print(paths)
                        self.iter_dict(data, paths)
                        print(self.returned_dict)

    def iter_dict(self, d,lists, itr = 0):
        print('/n/n/n/n/n')
        print(d.items())
        try:
            for k, v in d.items():
                print('\nk = {},\n lists = {}\n'.format(k, lists[itr]))
                
                #print(v)
                try:
                    if lists[itr] in k:
                        print('Lists = {}\nitr = {}'.format(lists,itr))

                        if itr>=len(lists):
                            if v in lists:
                                print('returning\n')
                                self.returned_dict[v] = d[v]
                            
                        elif isinstance(v, dict):
                            self.iter_dict(v,lists, itr+1)
                        
                        else:
                            print('*******')
                            print(k,v)
                            self.returned_dict[k] = v
                except RuntimeError as e:             
                    print(e, k, v)
        except RuntimeError as e:             
            print(e)

    def find_data(self, **kwargs):
        try:
            for key,value in kwargs.items():#ex. key=title, value=children
                #print('key value pair search for: {}'.format(value))
                if key=='json':
                    self.get_json(value)
                else:
                    if key not in self.returned_dict.keys():
                        high_pass = self.soup.find(value['find'][0], class_=value['find'][1])
                        if high_pass is not None:
                            low_pass = high_pass.find_all(value['find_all'])
                            first_value = low_pass[0].text
                            print(key)
                            print(low_pass)
                            #print("Found data {}".format(first_value))
                            if value['remove'][0]!='None':
                                for rm in value['remove']:
                                    #print('trying to remove {} from {}'.format(rm, key))
                                    if first_value.find(rm)!=-1:
                                        first_value = first_value.replace(rm, '')
                            data = {str(key):first_value.strip()}
                            self.returned_dict.update(data)
                            #print('data/dict: {}----{}'.format(data,returned_dict))
            print('RD***** = {}'.format(self.returned_dict))
            return self.returned_dict
        except RuntimeError as e:
            print(e)
            print('Error in finding data for {},{} pair'.format(key,value)) 