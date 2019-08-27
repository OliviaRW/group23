import requests, time, os, random, json, re, lemmy, datetime, collections

import pandas as pd 
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib

from bs4 import BeautifulSoup
from scraping_class import Connector

import seaborn as sns

colorpalette = 'hls'
sns.set_palette(colorpalette, 11)