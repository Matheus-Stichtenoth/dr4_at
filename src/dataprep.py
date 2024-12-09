import pandas as pd
import os
import json
import requests

path_deputados = 'https://dadosabertos.camara.leg.br/api/v2/deputados'

response = requests.get(path_deputados)
