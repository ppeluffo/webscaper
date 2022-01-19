#!/opt/anaconda3/envs/mlearn/bin/python
'''
Este script ejecuta un servicio con Selenium y accede a sitio de money.cnn
para scrapear y leer datos de los tickets, nombres, sectores, industrias, compatidores
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd

driver_path = '/opt/WebDriver/chromedriver'
root_url = 'https://money.cnn.com/data/us_markets/'

# Para correrlo como un servicio
#service = Service(executable_path=driver_path)
#driver = webdriver.Chrome(service=service)

# Para correrlo en modo individual
driver = webdriver.Chrome(driver_path)
driver.get(root_url)

# Localizo los stock sectors
stock_sectors = driver.find_element(By.XPATH,'//*[@id="wsod_sectorPerformance"]/table/tbody')
links = stock_sectors.find_elements(By.TAG_NAME,'a')
sectors_name = []
sectors_url = []
for link in links:
    sector_name = link.text
    sector_url = link.get_attribute("href")
    sectors_name.append( sector_name)
    sectors_url.append(sector_url)
    print('{0}, {1}'.format(sector_name, sector_url))
#
sectors = pd.DataFrame(data={'name':sectors_name, 'url':sectors_url})
# Recorremos los sectores
for sector_name, sector_url in sectors:
    driver.get(sector_url)
