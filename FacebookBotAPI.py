import facebook
import time
import os
import socket
from random import randint
from random import choice
from sentenceGenerator import SenGen

class FakeBook_API():
    def __init__(self, token, userId):
        self.log = open("logs/API_log_{}.csv".format(time.strftime("%m%d%y")), "a")
        self._id  = userId
        self.sengen = SenGen()

        try:
            self.graph = facebook.GraphAPI(token)
            self.profile = self.graph.get_object(userId)
        except Exception as e:
            self.writeLog("error occured while connecting: {}".format(e))
            return

        self.name = self.graph.get_object("me")["name"]
        self.startTime = time.time()
        print("{} connected to graph API".format(self.name))
        self.writeLog("{} connected to FB's Graph API".format(self.name))

    def postToWall(self):
        #Grabs a random sentence and posts it as a status
        msg = self.sengen.randSen()
        status = self.graph.put_wall_post(message=msg)
        print("{} posted a new status".format(self.name))
        self.writeLog("'{}' was written to {}'s wall".format(msg, self.name))

    def comment(self):
        #Posts a random comment on a random post on the users wall
        cmt = self.sengen.randSen()
        posts = self.graph.get_connections(self._id, "posts")
        randPost = posts['data'][randint(0,len(posts["data"])- 1)]['id']
        self.graph.put_comment(randPost, cmt)
        print("{} posted a comment".format(self.name))
        self.writeLog("'{}' was commented on post_id {}".format(cmt, randPost))

    def postPhoto(self):
        #Posts a random photo from the pics folder to the users wall.
        img = choice(os.listdir("pics"))
        with open("pics/" + img, "rb") as image:
            self.graph.put_photo(image)
        print("{} posted a random photo".format(self.name))
        self.writeLog("Random picture from pics posted to wall. photo name = {}".format(img))

    def randomRun(self):
        # Chooses a random method after waiting a random amount of time between 30 and 60 seconds
        # Below the tuples are (waitTime, totalTimeInSeconds)
        times = [(1, 30), (30, 600)]
        methods = [self.postToWall, self.comment, self.postPhoto]
        for wait, totalTime in times:
            print("starting next test of 3... Wait {} minutes".format(str(totalTime * 3 / 60)))
            for i in range(3):
                endTime = time.time() + totalTime
                while time.time() < endTime:
                    time.sleep(wait)
                    choice(methods)()

        print("Done!")


    def testRun(self):
        # Will run the same as randomRun but for each method
        methods = [self.postToWall, self.comment, self.postPhoto]
        times = [(1, 30), (30, 600)]

        for wait, totalTime in times:
            for method in methods:
                print("Running {} for {} minutes".format(str(method).split(" ")[2].split(".")[1], totalTime/60))
                self.writeLog("Running {} for {} minutes".format(str(method).split(" ")[2].split(".")[1], totalTime/60))
                endTime = time.time() + totalTime
                while time.time() < endTime:
                    time.sleep(wait)
                    method()
                self.writeLog("{} {} minute test done".format(str(method).split(" ")[1].split(".")[1], totalTime/60))

    def writeLog(self, desc):
        self.log.write("{},{},{},{}\n".format(int(time.time()), socket.gethostbyname(socket.gethostname()), socket.gethostbyname('www.facebook.com'), desc))

    def finish(self):
        self.writeLog("{} disconnected, Total session time was {} minutes\n".format(self.name, round(time.time() - self.startTime / 60)))
        self.log.close()

if __name__ == "__main__":
    fb = FakeBook_API(token="EAACEdEose0cBAPGhhDogmGXiajPYfGDYchjyZBhJgdKm9noBZChp3ygtWsJzi08n7liIXqD2ClVjuCm8ZBbZA9KOXxzWLKedsZA20PBjYvrYPMdmygUiZAEc9WJrnvABlAHPMmu7ZBjHtBJPB6npFRYNUVHfq0buU7uh48uOZAwzuKzonhyODbSNroPQA5dWvt8ZD",
                      userId="110342492928152")
    fb.randomRun()