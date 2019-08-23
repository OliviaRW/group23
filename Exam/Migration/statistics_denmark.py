import requsts, json
import numpy as np
import pandas as pd
from scraping_class import Connector

class dst_api:
    def __init__(self, logfile):
        self.connector = Connector(logfile)
    
    def get_data