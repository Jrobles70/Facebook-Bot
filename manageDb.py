import sqlite3

class manageDb:
    def __init__(self, name='Accounts.db'):
        self._db = sqlite3.connect(name)
        self.createCurs()

        self._c.execute("CREATE TABLE IF NOT EXISTS names(name TEXT, nameId INTEGER PRIMARY KEY, email TEXT, gender TEXT, status TEXT)")
        self._c.execute("CREATE TABLE IF NOT EXISTS FacebookLogs(nameId INTEGER, date TEXT, time INTEGER, log TEXT, FOREIGN KEY(nameId) REFERENCES names(nameId))")
        #c.execute("CREATE TABLE IF NOT EXISTS Facebook(nameId INTEGER, friends INTEGER, FOREIGN KEY(nameId) REFERENCES names(nameId))") Use for FB honeypot info
        #c.execute("CREATE TABLE IF NOT EXISTS Insta(nameId INTEGER, username TEXT, followers INTEGER, following INTEGER, FOREIGN KEY(nameId) REFERENCES names(nameId))") Use for instagram
        #c.execute("CREATE TABLE IF NOT EXISTS Insta_logs(nameId INTEGER, date TEXT, time INTEGER, log TEXT, FOREIGN KEY(nameId) REFERENCES names(nameId))")
        self.closeCurs()

    def createCurs(self):
        self._c = self._db.cursor()

    def closeCurs(self):
        self._db.commit()
        self._c.close()

    def getLog(self, date, start="", end="", table='FacebookLogs'):
        if not start and not end:
            self._c.execute("SELECT log FROM ? WHERE date = ?", (table, date))
        elif start and end:
            self._c.execute("SELECT log FROM ? WHERE date = ? AND time > start AND time < end", (table, date,start,end))
        log = self._c.fetchall()
        f = open(table[:-1] + str(date) + ".csv", "w")
        for line in log:
            f.write(line)
        f.close()

    def addNames(self, nameDict):
        nameId = self.getNextId()
        for key in nameDict:
            email, gender = nameDict[key]
            self._c.execute("INSERT INTO names VALUES(?, ?, ?, ?, ?)", (key, nameId, email, gender, "Not Created"))
            nameId += 1

    def updateEmail(self, name, newVal):
        self._c.execute("UPDATE names SET email = ? WHERE name = ?", (newVal, name))

    def updateStatus(self, email, new):
        self._c.execute("UPDATE names SET status = ? WHERE email = ?", (new, email))

    def getStatus(self, status):
        return self._c.execute("SELECT name, email FROM names WHERE status = ?", (status,)).fetchall()

    def getNextId(self):
        return len(self._c.execute("SELECT * FROM names").fetchall())

    def signupInfo(self, email):
        test = self._c.execute("SELECT name, gender FROM names WHERE email = ?", (email,)).fetchone()
        return test

    def getEmail(self, name):
        return self._c.execute("SELECT email FROM names WHERE name = ?", (name,)).fetchone()

    def getNotCreated(self, limit=0, noEmptyEmails=True):
        ex = "SELECT name, email FROM names WHERE status = 'Not Created'"
        if noEmptyEmails:
            ex += " AND email != ''"
        if limit > 0:
            ex += " LIMIT = {}".format(limit)

        return self._c.execute(ex).fetchall()

    def getNumAccounts(self):
        return len(self._c.execute("SELECT name FROM names WHERE status = 'Verified'").fetchall())
