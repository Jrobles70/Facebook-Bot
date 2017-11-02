from FacebookBotSEL import FakeBook_Sel, AccountBlockedError
from time import time, sleep
from random import choice, randint

class selTestCases(FakeBook_Sel):
    def __init__(self, name, email, password):
        FakeBook_Sel.__init__(self, name)
        self.email = email
        self.password = password
        self.writeLog("About to begin test cases...")

    def randomRun(self):
        self.signIn(self.email, self.password)
        self.writeLog("Beginning random run...")
        # Chooses a random method after waiting a random amount of time between 30 and 60 seconds
        # Below the tuples are (waitTime, totalTimeInSeconds)
        times = [(1, 30), (30, 600)]
        methods = [self.likePost, self.postToWall, self.comment, self.nextPage, self.share]
        for wait, totalTime in times:
            print("starting next test of 3... Wait {} minutes".format(str(totalTime * 3 / 60)))
            for i in range(3):
                endTime = time() + totalTime
                while time() < endTime:
                    sleep(wait)
                    randMethod = choice(methods)()
                    while randMethod == self.nextPage:
                        randMethod = choice(methods)()

        self.writeLog("Random run completed")
        self.finish()

    def testRun(self):
        self.signIn(self.email, self.password)
        self.writeLog("Beginning test run...")
        # Will run the same as randomRun but for each method
        methods = [self.postToWall, self.likePost, self.comment, self.nextPage, self.share]
        times = [(1, 30), (30, 600)]

        for wait, totalTime in times:
            for method in methods:
                print("Running {} for {} minutes".format(str(method).split(" ")[1].split(".")[1], totalTime / 60))
                self.writeLog(
                    "Running {} for {} minutes".format(str(method).split(" ")[1].split(".")[1], totalTime / 60))
                endTime = time() + totalTime
                while time() < endTime:
                    sleep(wait)
                    method()
                self.writeLog("{} {} minute test done".format(str(method).split(" ")[1].split(".")[1], totalTime/60))
        self.writeLog("Test run completed")
        self.finish()

    def quickSignIn(self):
        # This is to test an account being banned for signing in and out
        self.writeLog("Beginning quick sign in test..")
        start = time()
        endTime = start + 3*30 + 3*600

        try:
            while(start<endTime):
                sleep(randint(1,60))
                self.signIn(self.email, self.password)
                choice([self.postToWall, self.likePost, self.comment, self.nextPage, self.share])()
                self.finish()
        except AccountBlockedError:
            print("Account has been blocked. Ending test case")

        self.writeLog("Sign in test completed")

    def longTest(self, waitConstant=2):
        self.signIn(self.email, self.password)
        self.writeLog("Beginning long run with a wait constant of {} minutes...".format(waitConstant))
        # Chooses a random method after waiting a random amount of time between 30 and 60 seconds
        methods = [self.postToWall, self.likePost, self.comment, self.nextPage]
        runTimes = [3, 5, 10, 20]
        print("Starting part 1")
        self.writeLog("Starting part 1")

        for meth in methods:
            # Runs each action once and waits the amount of minutes given for wait constant after each
            meth()
            sleep(waitConstant * 60)
        print("Starting part 2")
        self.writeLog("Starting part 2")
        for run in runTimes:
            # Runs each method on a loop for each time (in minutes) in runTimes and waits for 5 seconds after each action
            count = 0
            start = time()
            end = start + (run * 60)

            while start < end:
                methods[count]()
                if count is len(methods) - 1:
                    count = 0
                else:
                    count += 1
                sleep(5)

            sleep(waitConstant * 60)

        start = time()
        end = start + (20*60)

        print("Starting part 3")
        self.writeLog("Starting part 3")

        while start < end:
            # Does a random action for for 20 minutes and waits a random amount of time between 1 and 60 seconds
            choice(methods)()
            sleepTime = randint(1, 60)
            self.writeLog("Sleeping for {} seconds".format(sleepTime))
            sleep(sleepTime)

        sleep(waitConstant * 60)
        self.writeLog("Long run has finished")

def main(name, email):
    pw = "U0NetSec"
    acc = selTestCases(name, email, pw)
    try:
        print("Press Control + C to stop at any time...")
        for i in range(1):
            acc.longTest()
        print("Done")
    except KeyboardInterrupt:
        acc.finish()
