from selenium import webdriver
from time import sleep

class SenGen:
    def __init__(self):
        # Connects to a website that generates random sentences
        self.driver = webdriver.PhantomJS("phantomjs.exe")
        self.driver.get('http://watchout4snakes.com/wo4snakes/random/randomsentence')

    def randSen(self):
        # Returns a random sentence
        button = self.driver.find_element_by_css_selector("input[type='submit'][value='Refresh']")
        button.click()
        sleep(1)
        sen = self.driver.find_element_by_id("result").get_attribute("innerHTML")
        return sen



