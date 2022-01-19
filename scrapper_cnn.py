#!/opt/anaconda3/envs/mlearn/bin/python

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import numpy as np
import time
import pandas as pd

driver_path='/opt/WebDriver/chromedriver'


class CNN:

    def __init__(self):
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.base_url = "https://money.cnn.com/data/us_markets/"
        self.actual_url = None
        self.d_tickets = None
        self.df_sectores = None
        self.df_industries = None

    def set_url_base(self, url=None):
        self.base_url = url

    def get_url_base(self):
        return self.base_url

    def get_actual_url(self):
        return self.actual_url

    def open(self, url=None):
        if url is None:
            self.actual_url = self.base_url
            self.driver.get(self.base_url)
        else:
            self.actual_url = url
            self.driver.get(url)

    def close(self):
        self.driver.close()

    def read_url(self,url=None, verbose=False):
        # Leo una url pero espero en forma aleatoria para no ser detectado como robot.
        st = np.random.randint(1, 5)
        print('Sleeping {} secs...'.format(st))
        time.sleep(st)
        if url is None:
            return False
        self.actual_url = url
        if verbose:
            print('Reading url={}'.format(url))
        self.driver.get(url)

    def read_sectors(self, file_name='sectores.csv'):
        '''
        Lee los sectores de un archivo
        '''
        print('Reading sectors from file...')
        self.df_sectores = pd.read_csv(file_name, index_col='sector')
        return self.df_sectores

    def scrap_sectors(self, verbose=False, save_to_file=False, file_name='sectores.csv'):
        '''
        Lee los sectores de la web y los deja en un df.
        '''
        if verbose:
            print('Scrapping Sectors...')
        start = time.time()
        self.read_url(url=self.base_url, verbose=verbose)
        links = self.driver.find_elements(By.XPATH, '//*[@id="wsod_sectorPerformance"]/table/tbody/tr/td/a')
        if not links:
            # Un empty sequence is false
            print('Select Elements by XPATH returns Empty !!')
            return
        #
        s_names=[]
        s_urls=[]
        for link in links:
            sector_name = link.text
            sector_link = link.get_attribute('href')
            s_names.append(sector_name)
            s_urls.append(sector_link)
            if verbose:
                print('{0} ==> {1}'.format(sector_name, sector_link))
        # Genero un DF con los datos
        self.df_sectores = pd.DataFrame(data={'sector':s_names, 'url':s_urls})
        self.df_sectores.set_index('sector',inplace=True)
        if save_to_file:
            self.df_sectores.to_csv(file_name)
        #
        end = time.time()
        print('Elapsed time: %0.3f secs.' % (end - start))
        return self.df_sectores

    def get_sectors(self):
        return self.df_sectores

    def read_industry(self, file_name='industries.csv'):
        print('Reading industries from file...')
        self.df_industries = pd.read_csv(file_name)
        return self.df_industries

    def scrap_industries(self, verbose=False, save_to_file=False, file_name='industries.csv'):
        start = time.time()
        if self.df_sectores is None:
            print('Primero debe leer los sectores !!')
            return
        if verbose:
            print('Scrapping industries...')

        industries = []
        for sector_name in self.df_sectores.index:
            sector_url = self.df_sectores.loc[sector_name, 'url']
            self.read_url(url=sector_url, verbose=verbose)
            try:
                dropdown = Select(self.driver.find_element(By.ID, 'wsod_industriesSelector'))
            except:
                print('ERROR: Element is not Select !!')
                return
            options = dropdown.options
            for opt in options:
                industry = opt.get_attribute('text')
                if verbose:
                    print('{0}:{1}'.format(sector_name, industry))
                industries.append({'sector': sector_name, 'industry': industry})
        #
        self.df_industries = pd.DataFrame(data=industries )
        if save_to_file:
            self.df_sectores.to_csv(file_name)
        #
        end = time.time()
        print('Elapsed time: %0.3f secs.' % (end - start))
        return self.df_industries

    def get_industries(self):
        return self.df_industries

    # --------------------------------------------
    def scrap_tickets(self, verbose=False):
        if self.l_sectors is None:
            print('Leyendo sectores')
            self.scrap_sectors(verbose=verbose)
        #
        # Leo todas las industrias de un sector viendo las opciones del dropdown
        for sector_name, sector_url in self.l_sectors:
            industries = []
            # Me voy a la pagina del sector
            if verbose:
                print('Sector: {}'.format(sector_name))
                print('Reading url {}'.format(sector_url))
            self.read_url(url=sector_url)
            # Hay una lista desplegable de las industrias. Extraigo cuantas tengo para dicho sector
            dropdown = Select(self.driver.find_element(By.ID, 'wsod_industriesSelector'))
            options = dropdown.options
            for opt in options:
                ind = opt.get_attribute('text')
                industries.append(ind)
            #
            self.d_tickets = dict()
            #
            # Recorro c/industria.
            # Voy seleccionado las industries y enfocandome en c/u para acceder a la tabla de tickets
            for i in range(len(options)):
                self.read_url(url=sector_url)
                dropdown = Select(self.driver.find_element(By.ID, 'wsod_industriesSelector'))
                dropdown.select_by_index(i)
                ticket_table = self.driver.find_element(By.XPATH, '//*[@id="wsod_companiesInIndustry"]')
                ticket_lines = ticket_table.find_elements(By.CLASS_NAME, 'wsod_symbol')
                # Cada ticket_line es un webelement.
                tck = dict()
                for item in ticket_lines:
                    ticket_name = item.get_attribute('text')
                    ticket_url = item.get_attribute('href')
                    #
                    tck['sector_name'] = sector_name
                    tck['sector_url'] = sector_url
                    tck['industrie_name'] = industries[i]
                    tck['ticket_url'] = ticket_url
                    self.d_tickets[ticket_name] = tck
                    if verbose:
                        print('{0},{1},{2},{3}'.format( ticket_name, tck['sector_name'], tck['industrie_name'], tck['ticket_url'] ))

    def get_tickets(self):
        return self.d_tickets