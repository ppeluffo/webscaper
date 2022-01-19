#!/opt/anaconda3/envs/mlearn/bin/python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
# import time
from selenium.webdriver.support.ui import WebDriverWait

driver_path='/opt/WebDriver/chromedriver'

url_base = 'https://www.adamchoi.co.uk/teamgoals/detailed'
# No lo arranco como service porque estoy en testing
#service=Service(executable_path=driver_path)
driver = webdriver.Chrome(driver_path)
page = driver.get(url_base)

# all_matches_btn = driver.find_element(By.XPATH,'//*[@id="page-wrapper"]/div/home-away-selector/div/div/div/div/label[2]' )
all_matches_btn = driver.find_element(By.XPATH,'//label[@analytics-event="All matches"]' )
all_matches_btn.click()

dropdown = Select(driver.find_element(By.ID,'country'))
dropdown.select_by_visible_text('Spain')
# time.sleep(5)

#tabla = driver.find_element(By.CLASS_NAME, "")
print('Busco matches')
td_elements = driver.find_elements(By.TAG_NAME, 'td')
for td in td_elements:
    print(td.text)

driver.quit()
exit(0)

matches = WebDriverWait(driver, timeout=10).until(lambda d: d.find_elements(By.TAG_NAME, "tr"))
#matches = driver.find_elements(By.TAG_NAME, "tr")

driver.quit()

#print(matches)
print("Largo matches = {}".format(len(matches)))
for match in matches:
    td_elements = match.find_elements(By.TAG_NAME, 'td')

    # Cada match es un webelement.
    #print(match.text)

print('Fin')