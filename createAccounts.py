from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from random import choice, randint
from manageDb import manageDb
from time import time, sleep
from os import listdir, getcwd
from math import ceil

class accountGen(manageDb):
    def __init__(self):
        manageDb.__init__(self)
        desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
        desired_capabilities['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' \
                                                         'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                                         'Chrome/39.0.2171.95 Safari/537.36'
        #service_args = ['--proxy=127.0.0.1:9999', '--proxy-type=socks5']
        self.driver = webdriver.PhantomJS("phantomjs.exe", desired_capabilities=desired_capabilities)
        self.driver1 = webdriver.PhantomJS("phantomjs.exe", desired_capabilities=desired_capabilities)
        self.password = "U0NetSec"
        self.driver.set_window_size(1024, 768)

    def getInfo(self, number=100):
        self.createCurs()
        nameDict = {}
        for i in range(2,4):
            if i == 2:
                gender = "m"
            else:
                gender = "f"

            self.driver.get('http://random-name-generator.info/random/?n={}&g={}&st=2'.format(number, i))


            for j in range(1, ceil((number + 1)/2)):
                name = self.driver.find_element_by_xpath('//*[@id="main"]/div[3]/div[2]/ol/li[{}]'.format(j))
                name = name.get_attribute("innerHTML").split(" ")
                name = "{} {}".format(name[0][5:-4], name[1][4:-6])
                print("adding {}".format(name))
                nameDict[name] = ["", gender]
        self.addNames(nameDict)
        self.closeCurs()

    def test(self):
        self.driver.get("http://www.google.com")
        self.driver.find_element_by_xpath('//*[@id="lst-ib"]').send_keys("HELLO WORLD")
        self.driver.find_element_by_xpath("//div[text()='Update Profile Picture']")
    def makeEmail(self, numAccounts=0):
        self.createCurs()
        nameLi = self.getStatus("Not Created")
        if len(nameLi) < numAccounts:
            print("Grabbing more info")
            self.getInfo(numAccounts - len(nameLi))

        for i in range(numAccounts):
            print("Starting accountGen")
            self.driver1.get('https://temp-mail.org/en/option/change/')
            input = self.driver1.find_elements_by_xpath('//*[@id="mail"]')
            name = nameLi[i][0].split(" ")
            email = "{}_{}".format(name[0], name[1])
            input[1].send_keys(email)
            self.driver1.find_element_by_xpath('//*[@id="postbut"]').click()
            wholeEmail = self.driver1.find_elements_by_xpath('//*[@id="mail"]')[0].get_attribute("value")
            self.updateEmail("{} {}".format(name[0], name[1]), wholeEmail)
            self.createAccount(wholeEmail)

    def createAccount(self, email):
        self.createCurs()
        password = "U0NetSec"
        name, gender = self.signupInfo(email)
        first, last = name.split(" ")
        self.driver.get('https://facebook.com/')
        boxes = self.driver.find_elements_by_css_selector("[id*=u_0_]")

        for box in boxes:
            boxName = box.get_attribute("name")
            try:
                if boxName == "firstname":
                    box.send_keys(first)
                elif boxName == "lastname":
                    box.send_keys(last)
                elif boxName != None and "reg_email__" in boxName:
                    box.send_keys(email)
                elif boxName == "reg_email_confirmation__":
                    conf = box
                elif boxName == "websubmit":
                    submit = box
                elif boxName == "reg_passwd__":
                    box.send_keys(password)
                elif boxName == "sex":
                    id = box.get_attribute("id")
                    if "6" in id and gender == "f":
                        sex = box
                    elif "7" in id and gender == "m":
                        sex = box
                    else:
                        sex = box
            except Exception as e:
                print(boxName)
                print(e)

        conf.send_keys(email)
        sex.click()
        month = self.driver.find_element_by_xpath('//*[@id="month"]')
        month.click()
        month.send_keys("J")
        day = self.driver.find_element_by_xpath('//*[@id="day"]')
        day.click()
        day.send_keys(randint(1, 30))
        year = self.driver.find_element_by_xpath('//*[@id="year"]')
        year.click()
        year.send_keys("1995")
        submit.click()
        sleep(10)

        if self.onConfirmation():
            code = self.getVerification(email)
            inputBox = self.driver.find_element_by_xpath('//*[@id="code_in_cliff"]')
            inputBox.send_keys(code)
            inputBox.send_keys(Keys.ENTER)
            if self.isCaptcha():
                print("{}'s account needs to be verified with a phone number".format(name))
                self.updateStatus(email, 'Needs phone verification')
            else:
                print(email)
                self.updateStatus(email, 'Account Created')
                self.driver.save_screenshot('VERIFYACCOUNT.jpg')

        self.closeCurs()

    def submitPhoto(self, email):
        img = "{}\\pics\\{}".format(getcwd(), choice(listdir("pics")))
        self.driver.find_element_by_id('photo_input').click()
        self.driver.find_element_by_xpath('//*[@id="photo_input"]').send_keys(img)
        self.driver.find_element_by_xpath('//*[@id="checkpointSubmitButton-actual-button"]').click()
        # TODO: Verify that the photo has been submitted
        # Text box appears on random element id but one should be
        # //*[@id="u_0_a"]
        # " You Can't Log In Right Now"
        self.updateStatus(email, 'Photo Submitted')

    def getVerification(self, email):
        self.createCurs()
        email = email.split("@")[0]
        self.driver1.get('https://temp-mail.org/en/option/change/')
        input = self.driver1.find_elements_by_xpath('//*[@id="mail"]')
        input[1].send_keys(email)
        post = self.driver1.find_element_by_xpath('//*[@id="postbut"]')
        post.click()

        timeout = 60 + time()
        while True:
            if time() > timeout:
                print("Timeout activated verification was not found")
                break
            self.driver1.get('https://temp-mail.org/en/option/refresh/')
            try:
                code = self.driver1.find_element_by_xpath('//*[@id="mails"]/tbody/tr/td[2]/a').get_attribute('innerHTML')
                if 'is your Facebook co' in code:
                    code = code.split(" ")[0]
                return code
            except NoSuchElementException:
                sleep(2)
        self.closeCurs()

    def onConfirmationMbasic(self):
        try:
            text = self.driver.find_element_by_xpath('//*[@id="m_conf_cliff_root_id"]/div/div/div[1]/span').get_attribute('innerHTML')
            if text == 'Let us know this email belongs to you. Enter the code in the email sent to':
                return True
        except NoSuchElementException:
            return False
    def onConfirmation(self):
        try:
            text = self.driver.find_element_by_xpath('//*[@id="content"]/div/div/div[1]/div[1]/div/div[2]/h2').get_attribute('innerHTML')
            if text == 'Enter the code from your email':
                return True
        except NoSuchElementException:
            return False

    def isCaptcha(self):
        try:
            self.driver.find_element_by_xpath('//*[@id="captcha"]/div/a').get_attribute('innerHTML') == 'Enter a mobile number'
            return True
        except NoSuchElementException:
            return False

    def isFlagged(self):
        # Returns true if account is flagged for suspicious activity
        try:
            self.driver.find_element_by_xpath('//*[@id="u_0_0"]/div[1]/div[2]/span')
            return True
        except NoSuchElementException:
            return False

#Enter information/finish signup
#profile/cover photo?
#liking/following pages(Should be in FacebookSEL)

if __name__ == "__main__":
    test = accountGen()
    test.makeEmail(2)
