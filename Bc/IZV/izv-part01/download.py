#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from zipfile import ZipFile
import os
import sys
import requests
import csv
import pickle
import gzip
from bs4 import BeautifulSoup
from io import TextIOWrapper

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a", "region"]
    
    dtypes = [ "int32", "i8", "int16", "M8", "U16", "int16", "i8", "i8", "i8", "i8", "i8", "i8", "int16", "i8", # < 14
                "i8", "i8", "i8", "i8", "i8", "i8", "i8", "i8", "i8", "i8", "i8","i8","i8","i8", "i8", # 14 < 29
                "i8","i8","i8","i8","i8", "i8","i8","i8","i8","i8","i8","i8","i8", "i8", # < 43
                "i8","i8","f8","f8","f8","f8","f8","f8","U16", "U16","U16","U16","U16","U16","U16","U16","U16","U16","U16","U16","i8", "U16"]
                
    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    regionsData = {
        "PHA": None,
        "STC": None,
        "JHC": None,
        "PLK": None,
        "ULK": None,
        "HKK": None,
        "JHM": None,
        "MSK": None,
        "OLK": None,
        "ZLK": None,
        "VYS": None,
        "PAK": None,
        "LBK": None,
        "KVK": None,
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.folder = folder
        self.url = url
        self.cache_filename = cache_filename

    def download_data(self):
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
        with requests.Session() as session:
            data = session.get(self.url)
            soup = BeautifulSoup(data.content, 'html.parser')
            rows = soup.findAll("tr")
            for row in rows:
                cells = row.find_all("td")
                cell = cells[-1]
                iterator = -1
                while (cell.text != "ZIP"):
                    iterator -= 1
                    cell = cells[iterator]
                button = cell.find("button")
                link = button.get('onclick')
                link = link.strip("download").strip("('").strip("')") #remove function name and '('')'
                filename = link[5:] #remove path
                file = session.get(self.url + link)
                with open(self.folder + "/" + filename, 'wb') as f:
                    f.write(file.content)
            
    def parse_region_data(self, region):
        newDict = {}
        for i in range(len(self.headers)):
            newDict[self.headers[i]] = []
        if not os.path.exists(self.folder) or not os.listdir(self.folder):
            self.download_data()
        csvFileName = self.regions.get(region, False)
        if not csvFileName:
            sys.exit("region code not valid")
        csvFileName += ".csv"
        for fileZip in os.scandir(self.folder):
            if fileZip.name.endswith(".zip"):
                with ZipFile(fileZip, 'r') as zip:
                    csvFile = zip.open(csvFileName, 'r')
                    spamreader = csv.reader(TextIOWrapper(csvFile, encoding='cp1250'), delimiter=';')
                    for row in spamreader:
                        for i, val in enumerate(row):
                            #check for invalid values
                            if val in {"", "XX", "A:", "B:", "C:", "D:", "E:", "F:", "G:", "-"}:
                                newDict[self.headers[i]].append(-1)
                            else:
                                val = val.replace(",", ".")
                                newDict[self.headers[i]].append(val)
        #transform dict of lists to dictionary of np.arrays
        for i, key in enumerate(newDict):
            newDict[key] = np.asarray(newDict[key], dtype=self.dtypes[i])
            
        newDict['region'] = np.full(newDict.get(self.headers[0]).size, region, dtype=self.dtypes[-1])
        return newDict
                
    def get_dict(self, regions=None):
        dictionary = {}
        newDict = {}
        listOfRegions = []
        maxLength = 0
        #prepare dictionary
        for i in range(len(self.headers)):
            newDict[self.headers[i]] = []
        #if arg empty
        if not regions:
            regions = self.regions.keys() #for all regions
        #get data from various sources cache/memory/internet
        for region in regions:
            cachePath = self.folder + "/" + self.cache_filename.format(region)
            if (self.regionsData.get(region)): 
                #data are in memory
                regionDictionary = self.regionsData.get(region)
            elif (os.path.exists(cachePath)): 
                # data are in cache
                with gzip.open(cachePath, 'rb') as cachehandler:
                    #get data from pkl.gz type cached file
                    regionDictionary = pickle.load(cachehandler)
            else:   
                #  needs to download data
                regionDictionary = self.parse_region_data(region)
                with gzip.open(cachePath, 'wb') as cachehandler:
                    #create pkl.gz type cache
                    pickle.dump(regionDictionary, cachehandler)
                self.regionsData[region] = regionDictionary    
            maxLength = max(maxLength, len(regionDictionary["p1"])) #get max lenght of array from all the data so the arrays are the same length
            listOfRegions.append(regionDictionary)
        
        #make all regions same lenght
        for regDict in listOfRegions:
            for i, key in enumerate(regDict):
                regDict[key] = np.pad(regDict[key], (0, maxLength-len(regDict[key])), 'constant', constant_values=(-1))
        
        # tady se to dava do jednoho, finalniho slovniku      
        for i in range(len(self.headers) ):
            valuesArray = []
            for region in listOfRegions:
                valuesArray.append(region.get(self.headers[i]))
            dictionary[self.headers[i]] = np.asarray(valuesArray)
            
        return dictionary  

# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
if __name__ == '__main__':
    downloader = DataDownloader()
    regionsToDownload = ["PHA", 'STC', 'KVK']
    dictionary = downloader.get_dict(regionsToDownload)
    print("Downloaded regions: " + ", ".join(regionsToDownload))
    print("Number of records: " + str(len(dictionary["p1"][0])))
    print("Name of columns: " + ", ".join(dictionary.keys()))
