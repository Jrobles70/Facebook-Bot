from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from random import choice
from random import randint
import socket
from sentenceGenerator import SenGen
from sys import exit
from createAccounts import accountGen


class FakeBook_Sel(accountGen):
    def __init__(self, name):
        """
        :param name:  string used to write events on the log.
        Description:  This class is used to create a headless browser that connects to and controls a single facebook
        account. It is able to post to its own wall, comment on other posts, and message and invite other
        people to be its friend.
        """
        accountGen.__init__(self)
        self.name = name
        self.sengen = SenGen()
        self.log = open("logs/SEL_log_{}.csv".format(time.strftime("%m%d%y")), "a")
        self.running = True

        # Input location of phantomjs below

        self.driver.set_window_size(1024, 768)  # optional
        self.reset()
        self.startTime = time.time()
        self.writeLog("{}: driver connected to facebook".format(self.name))

    def signIn(self, email, password):
        """
        :param email: username/email to be used to sign user in
        :param password: passwork to account
        :description: Signs the user in, confirms that sign in was a success, checks if account is banned
        """

        try:
            self.email = email
            em = self.driver.find_element_by_name("email")
            em.send_keys(email)
            pw = self.driver.find_element_by_name("pass")
            pw.send_keys(password)
            pw.send_keys(Keys.RETURN)
            if self.isSignedIn():
                self.writeLog("{}: signed into facebook \n".format(self.name))
                self.suggestionsPage()
            else:
                self.writeLog("{}: Something went wrong signing in".format(self.name))
                raise NoSuchElementException

            if self.isFlagged():
                self.createCurs()
                self.writeLog("{}: account is flagged. Submitting photo\n".format(self.name))
                self.updateStatus(self.email, "Needs Verification")
                self.running = False
                self.closeCurs()
                return

        except NoSuchElementException:
            self.writeLog("{}: Tried to sign in and failed. "
                          "Confirm sign in params and try again. {}, {}".format(self.name, email, password))

        self.updateStatus(self.email, "Verified")
        self.reset()

    def postToWall(self):
        """
        :description: Posts a random sentence as a status. Will try twice if an error occurs the first time.
        """

        text = self.sengen.randSen()
        for i in range(1):
            try:
                textbox = self.driver.find_element_by_name("xc_message")
                textbox.send_keys(text)
                submit = self.driver.find_element_by_name("view_post")
                submit.click()
                if self.postBlocked(text):
                    # If this runs it means facebook has put a temporary block on posting
                    break
                self.writeLog("{}: posted \"{}\" to wall \n".format(self.name, text))
                self.reset()
                break
            except NoSuchElementException:
                # If this occurs then it was not on the right page. It will refresh and try again
                # If it fails again it will finish because something is wrong.
                if i == 0:
                    self.writeLog("{}: There was an error finding the element to post status. Refreshing then again"
                          .format(self.name))
                    self.reset()
                else:
                    self.writeLog("{}: Element cannot be found. Taking screenshot and closing driver".format(self.name))
                    self.screenShot("postToWall")
                    self.finish()

    def likePost(self):
        """
        :description: Likes a random post on the current page. It checks to see if it has already liked the current post
        and will continue until it finds one even if it has to scroll to the next page.
        TODO: Add a way to grab the information on the post that is being liked. This is an issue because the like
              button has a different id that does not seem to correlate with the rest of the post.
        """
        # failsafe is used as a way to make sure that the loop does not get stuck in the loop if it continues to fail
        failSafe = 0
        while True:
            try:
                like = self.driver.find_elements_by_css_selector("[id^=like_]")
                likeIds = [x.get_attribute("id") for x in like]
                pick = choice(likeIds)

                if self.isLiked(pick):
                    raise AlreadyLikedError
                # Grabs all like buttons
                button = self.driver.find_element_by_xpath('//*[@id="{}"]/a[2]'.format(pick))
                button.click()
                if "reactions" in self.driver.current_url:
                    # The reaction and like button are not always in the same spot.
                    # If this clicks a react button it will choose a random reaction

                    num = randint(1,6)
                    # Xpath of reation buttons the only difference in the number that is formatted in
                    self.driver.find_element_by_xpath('//*[@id="root"]/table/tbody/tr/td/ul/li[{}]/table/tbody/tr/td/a/div/table/tbody/tr/td[2]'.format(num)).click()
                    self.writeLog("{}: reacted to a post".format(self.name))
                else:
                    self.writeLog("{}: liked a post".format(self.name))
                self.reset()
                break
            except AlreadyLikedError:
                # Removes the id of the post that has already been liked
                likeIds.remove(pick)
                if len(likeIds) is 0:
                    # If len == 0 then it has tried every post and must continue to the next page
                    self.writeLog("{}: All posts are liked on this page. Going to next page and trying again"
                                  .format(self.name))
                    self.nextPage()
                    likeIds = [x.get_attribute("id") for x in like]
                pick = choice(likeIds)
            except (IndexError, NoSuchElementException):
                # Index errors and NoSuchElementExceptions are rare and mainly occur when an account is on the wrong
                # page. In this care I will reset the page and try again
                if failSafe > 1:
                    self.writeLog("{}: Failsafe activated while trying to like. Need to Debug".format(self.name))
                    self.screenShot("{}_failsafeLike".format(self.name))
                    pass
                    #self.finish()
                failSafe += 1
                self.writeLog("{}: There was an error finding the element to like. Resetting page and trying again."
                      .format(self.name))
                self.reset()

    def comment(self):
        """
        :Description: Comments a random sentence on a random comment on the current page.
        """
        failSafe = 0
        while True:
            try:
                cmt = self.sengen.randSen()
                posts = self.driver.find_elements_by_css_selector("[id*=u_0_]")
                postIds = [x.get_attribute("id") for x in posts]
                pick = choice(postIds)
                if self.canComment(pick):
                    raise CommentNotAllowed
                self.driver.find_element_by_xpath('//*[@id="{}"]/div[2]/div[2]/a[1]'.format(pick)).click()
                inputBox = self.driver.find_element_by_id("composerInput")
                inputBox.send_keys(cmt)
                inputBox.send_keys(Keys.ENTER)
                self.writeLog("{}: wrote the comment {} on post {}".format(self.name, cmt, self.driver.current_url))
                self.reset()
                break
            except CommentNotAllowed:
                postIds.remove(pick)
                pick = choice(postIds)
            except (IndexError, NoSuchElementException) as e:
                if failSafe > 1:
                    self.writeLog("{}: Failsafe activated while trying to comment. Need to Debug. ERROR: {}"
                                  .format(self.name, e))
                    self.screenShot("{}_failsafeComment".format(self.name))
                    #self.finish()
                    pass

    def nextPage(self):
        """
        :description: Chooses the next page button on the wall feed. will run twice in the case the first time fails.
                      If it fails a second time something is wrong and the driver will close
        """
        for i in range(1):
            try:
                self.driver.find_element_by_xpath('//*[@id="m_newsfeed_stream"]/a').click()
                self.writeLog("{}: went to the next page".format(self.name))
            except NoSuchElementException:
                if i is 1:
                    self.writeLog("{}: Failsafe activated while trying to comment. Need to Debug."
                                  .format(self.name))
                    self.screenShot("{}_failsafeNextPage".format(self.name))
                    pass
                    #self.finish()
                self.reset()

        print("{}: On next page".format(self.name))

    def share(self):
        try:
            postIds = [x.get_attribute("id") for x in self.driver.find_elements_by_css_selector("[id*=u_0_]")]
            pick = choice(postIds)
            failsafe = 0
            while True:
                try:
                    self.driver.find_element_by_xpath('//*[@id="{}"]/div[2]/div[2]/a[2]'.format(pick)).click()
                    poster = self.driver.find_element_by_xpath('//*[@id="composer_form"]/div[3]/div/div[2]/div/span'
                                                               .format(pick)).get_attribute("innerHTML")

                    post = self.driver.find_element_by_xpath('//*[@id="composer_form"]/div[3]/div/div[2]/span'
                                                             .format(pick)).get_attribute("innerHTML")
                    self.driver.find_element_by_name("view_post").click()

                    if self.shareBlocked():
                        raise ShareRequestDeniedError

                    self.writeLog("{}: shared post {}: {}".format(self.name, poster, post))
                    self.reset()
                    break
                except ShareRequestDeniedError:
                    self.writeLog("{}: Sharing has been temporarily blocked".format(self.name))
                    break
                except NoSuchElementException:
                    self.reset()
                    postIds.remove(pick)
                    if len(postIds) is 0:
                        failsafe += 1
                        if failsafe is 2:
                            self.screenShot("ShareFailsafe_{}".format(time.time()))
                            self.writeLog("Sharing failsafe activated. There were not elements to share")
                            break
                        postIds = [x.get_attribute("id") for x in self.driver.find_elements_by_css_selector("[id*=u_0_]")]
                    pick = choice(postIds)
        except IndexError:
            self.writeLog("{}: There was an error finding an element to share. Continuing to next method"
                          .format(self.name))
            self.screenShot("{}share".format(self.name))
            self.reset()

    def screenShot(self, picName):
        # Takes screeshot for debugging purposes
        self.driver.save_screenshot('debug/{}.png'.format(picName))

    def reset(self):
        # Brings driver back to main feed
        self.driver.get('https://mbasic.facebook.com')
        self.writeLog("{}: Page refreshed".format(self.name))

    def isSignedIn(self):
        # If error occurs that means the user has left the sign in page so the method returns true
        try:
            self.driver.find_element_by_name("email")
            return False
        except NoSuchElementException:
            return True

    def canComment(self, postId):
        # Returns true if a post is able to commented on
        try:
            self.driver.find_element_by_xpath('//*[@id="{}"]/div[2]/div[2]/a[1]'.format(postId))
            return False
        except NoSuchElementException:
            return True

    def suggestionsPage(self):
        # Skips facebooks suggested friends and settings
        try:
            while True:
                self.driver.find_element_by_xpath('//*[@id="root"]/div[1]/table/tbody/tr/td[3]/a').click()
                self.writeLog("{}: Getting off suggestion page".format(self.name))
        except NoSuchElementException:
            return

    def postBlocked(self, post):
        # Returns true if the account is post blocked
        try:
            status = self.driver.find_element_by_xpath('//*[@id="u_0_1"]/div[1]/div[2]/span/div')\
                .get_attribute('innerHTML')
            return not status == post
        except NoSuchElementException:
            self.writeLog("{}: Account tried to post status but is blocked from posting for a few minutes."
                          .format(self.name))
            return True

    def shareBlocked(self):
        # Returns true if account is directed to the screen that says it cannot share
        try:
            self.driver.find_element_by_xpath('//*[@id="root"]/div[1]/span')
            return True
        except NoSuchElementException:
            return False

    def isLiked(self, likeId):
        # Returns True is element is already liked
        try:
            self.driver.find_element_by_xpath('//*[@id="{}"]/a[2]/b'.format(likeId))
            return True
        except NoSuchElementException:
            return False

    def postPhoto(self):
        # TODO: Add method
        pass

    def changeProfilePicture(self):
        # TODO: Add method
        pass

    def finish(self):
        # Closes users driver
        self.driver.quit()
        self.writeLog("{}: driver disconnected, Total session time was {} minutes\n"
                      .format(self.name, round((time.time() - self.startTime) / 60, 2)))
        self.log.close()

    def writeLog(self, desc):
        # Writes log with (Unix time stamp, User Ip, Source Ip, description)
        line = "{},{},{},{}".format(int(time.time()),
                                              socket.gethostbyname(socket.gethostname()),
                                              socket.gethostbyname('mbasic.facebook.com'), desc)
        self.log.write(line)
        print(line)


class AccountBlockedError(Exception):
    # Made so I can have a custom error when accounts are found to be blocked
    pass


class AlreadyLikedError(Exception):
    # Made so I can tell when a post is already liked
    pass


class ShareRequestDeniedError(Exception):
    # Is raised when fb redirects to a page saying a post was not shared
    pass


class CommentNotAllowed(Exception):
    # Facebook has blocks on your feed that is not commentable
    # ex. Friend Suggestions, suggestions, etc.
    pass