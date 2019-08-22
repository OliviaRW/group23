from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

def get_counter_links(cities):
    response = requests.get('http://www.bicyclecounter.dk/BicycleCounter/BC_cykelbarometer.jsp')
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features='lxml')

    a_tags = soup.find_all('a', attrs = {'class': 'barbody'})
    return [a['href'] for a in a_tags if a.parent.contents[0] in cities]
    
def get_counter_data(counterlink, years, start = '1/1', end = '31/12'):
    driver = webdriver.Chrome('/Users/sebastianbaltser/Dropbox/Python/chromedriver')
    driver.get('http://www.bicyclecounter.dk/BicycleCounter/BC_KBH.jsp')
    driver.find_element_by_css_selector("a[href='BC_Statistics.jsp']").click()
    time.sleep(2)

    button = driver.find_element_by_css_selector("a[href='BC_Historical.jsp']")
    driver.execute_script("arguments[0].scrollIntoView();", button) #The element needs to be in view for it to be clicked
    button.click()
    time.sleep(2)

    for year in years:
        try:
            driver.find_element_by_css_selector("input[type='checkbox'][value='{}']".format(year)).click()
        except NoSuchElementException:
            print('Data for year {0} is not present for {1}'.format(year, counterlink))

    driver.find_element_by_css_selector("input[type='radio'][value='3']".format(year)).click()

    periodstart = driver.find_element_by_css_selector("input[type='text'][name='txtPeriodStart']".format(year))
    periodstop = driver.find_element_by_css_selector("input[type='text'][name='txtPeriodStop']".format(year))
    periodstart.clear()
    periodstart.send_keys(start)
    periodstop.clear()
    periodstop.send_keys(end)

    driver.find_element_by_css_selector("input[type='checkbox'][name='chkSendMail']".format(year)).click()
    mail = driver.find_element_by_css_selector("input[type='text'][name='txtEmail']".format(year))
    mail.clear()
    mail.send_keys('sebastian.baltser@gmail.com')

    driver.find_element_by_css_selector("input[type='image'][src='graphics/buttons/klik_for_rapport.gif']").click()

    driver.quit()

if __name__ == "__main__":
    counter_links = get_counter_links(['Copenhagen', 'Aalborg', 'Helsingør', 'Favrskov', 'Esbjerg'])
    for link in counter_links:
        get_counter_data(link, years = [2017, 2016, 2015, 2014])