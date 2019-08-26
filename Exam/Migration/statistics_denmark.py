import requests, json
import numpy as np
import pandas as pd
from scraping_class import Connector

class dst_api():
    def __init__(self, logfile):
        self.connector = Connector(logfile)
        self.delay = 0.5
    
    def get_data(self, url, filename, column = None, project_name = 'DST data collection'):
        response, _ = self.connector.get(url, project_name = project_name)
        text = json.loads(response.text)
        dataset = text['dataset']
        
        index = list(dataset['dimension']['Tid']['category']['index'].keys())
        data = dataset['value']

        pds = pd.Series(data = data, index = index, name = column)
        pds.index.name = 'Date'
        pds.to_csv(filename, header = True, index = True)

if __name__ == "__main__":
    dst_api_ = dst_api('dr_log.csv')

    url = r'https://api.statbank.dk/v1/data/VAN5/JSONSTAT?valuePresentation=Value&timeOrder=Ascending&ASYLTYPE=BRU&Tid=%3E%3D2007K1'
    filename = 'asylansøgninger.csv'
    dst_api_.get_data(url, filename, column = 'Asylansøgninger')

    url = r'https://api.statbank.dk/v1/data/VAN77/JSONSTAT?valuePresentation=Value&timeOrder=Ascending&OPHOLD=sum(12)&Tid=%3E%3D2007K1'
    filename = 'opholdstilladelser.csv'
    dst_api_.get_data(url, filename, column = 'Opholdstilladelser')