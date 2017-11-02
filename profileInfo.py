from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from FacebookBotSel import FakeBook_Sel

class enterInfo(FakeBook_Sel):
    def __init__(self, driver):
        self.driver = driver

    def veriProcess(self):
        elements = self.driver.find_elements_by_css_selector("[id*=u_0_]")
        for el in elements:
            try:
                if el.get_attribute("innerHTML") == "Next":
                    el.click()
            except Exception as e:
                print(e)
    def addProfilePic(self):
        # Add profile picture
    def addBots(self):
        # Find other bot accounts
    def enterInfo(self):
        # Enter page info
    def likePages(self):
        # Like new pages (Only most popular)
    def finish(self):
        # Run random activity for amount of time to try to be less suspicious
