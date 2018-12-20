#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 23:13:41 2018
@author: lewisclark
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import os
import requests

searchTerm = 'kew gardens 50p'  # will also be the name of the folder
url = "https://www.google.co.in/search?q=" + searchTerm + "&source=lnms&tbm=isch"
# NEED TO DOWNLOAD CHROMEDRIVER, insert path to chromedriver inside parentheses in following line
browser = webdriver.Chrome("/Users/lewisclark/experiments/chromedriver")
browser.get(url)
outputPath = "/Users/lewisclark/Documents/KewGardensPics"
goodImageExtensions = ["jpg", "jpeg", "png", "gif", "bmp"]
foundImageExtensions = set()

if outputPath == "":
    outputPath = searchTerm

if not os.path.exists(outputPath):
    os.mkdir(outputPath)

counter = 0
successfulCounter = 0
iterations = 5

print("Total pics to get: ", iterations * 400)

for y in range(iterations):
    for z in range(500):
        browser.execute_script("window.scrollBy(0,10000)")

    for x in browser.find_elements_by_xpath('//div[contains(@class,"rg_meta")]'):
        print("URL:", json.loads(x.get_attribute('innerHTML'))["ou"])

        img = json.loads(x.get_attribute('innerHTML'))["ou"]
        imgtype = json.loads(x.get_attribute('innerHTML'))["ity"]

        foundImageExtensions.add(imgtype)
        counter += 1

        if imgtype not in goodImageExtensions:
            continue

        try:
            raw_img = requests.get(img, stream=True)
            with open(os.path.join(outputPath, searchTerm + "_" + str(counter) + "." + imgtype), "wb") as f:
                for chunk in raw_img:
                    f.write(chunk)
            successfulCounter += 1

        except:
            print("bad download")

        print("Total Count:", counter)
        print("Successful Count:", successfulCounter)
        print()

print(successfulCounter, "pictures successfully downloaded")
print(foundImageExtensions)
browser.close()