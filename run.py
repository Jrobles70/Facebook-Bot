from FacebookBotSEL import FakeBook_Sel, AccountBlockedError
from runSEL import runMulti
import click
from time import time
from sys import exit
from time import sleep
from random import choice, randint
from manageDb import manageDb
#

@click.command()
@click.option('--length', '-l', prompt='length in seconds. 0 to run once.', default=60, help="set length to run")
@click.option('--interval', '-i', prompt='time between each action in seconds', default=5, help="set time in between each action. Use two numbers to have a random interval between them")
@click.option('--run', '-r', default='', multiple=True, help='runs a single action or actions for specific length with a specific interval.')
@click.option('--random', '-rand', default=False, is_flag=True, help='The order of the actions will be in random order')
@click.option('--multi', '-m', prompt='number of accounts to run', default=1, help='number of accounts to use')

def main(length, interval, run, random, multi):
    print("Press Control + C to cancel")
    DB = manageDb()
    DB.createCurs()
    max = DB.getNumAccounts()

    if multi < 1 or multi > max:
        print("Enter valid number for multiple accounts(Max={})".format(max))
        exit(0)

    botLi = {}

    for action in run:
        confirm(action)

    if type(interval) == list and len(interval) > 2:
        print("Too many numbers in interval")
        exit(0)

    accounts = DB.getStatus("Verified")

    for info in accounts:
        name, email = info
        bot = FakeBook_Sel(name)
        try:
            bot.signIn(email, "U0NetSec")
            if not bot.isSignedIn():
                # If this runs it means all accounts failed to sign in
                bot.writeLog("Account failed to log in. Closing driver")
                bot.finish()
            elif not bot.running:
                bot.finish()
            else:
                botLi[name] = bot
            if len(botLi) == multi:
                break
        except AccountBlockedError:
            bot.writeLog("Trying next account")
            bot.finish()

    if len(botLi) == 0:
        print("No accounts were able to sign in properly")
        exit(0)

    elif len(botLi) < multi:
        print("Only {} accounts were able to sign in".format(len(botLi)))

    if multi == 1:
        performAction(next(iter(botLi.values())), length, interval, run, random)
    else:
        runMulti(botLi, performAction, length, interval, run, random)

def confirm(action):
    try:
        action.lower() in ["post", "like", "comment", "share", "next"]
    except KeyError:
        print("{} is not a valid command".format(action))
        exit()

def performAction(bot, length, interval, run, random):
    methods = {
        "post": bot.postToWall,
        "like": bot.likePost,
        "comment": bot.comment,
        "share": bot.share,
        "next": bot.nextPage
    }
    if run:
        if run[0] == "all":
            print("changing run")
            run = ["post", "like", "comment", "share", "next"]
        else:
            run = run.split(" ")
            for action in run:
                print("confirming")
                confirm(action)

        if length == 0:
            for action in run:
                print(action)
                methods[action]()
                if len(interval) == 2:
                    sleep(randint(interval[0], interval[1]))
                else:
                    sleep(interval)
        else:
            endTime = time() + length
            while time() < endTime:
                for action in run:
                    if random:
                        methods[choice(run)]()
                    else:
                        methods[action]()
                    if len(interval) == 2:
                        sleep(randint(interval[0], interval[1]))
                    else:
                        sleep(interval)

            print("Done!")
        bot.finish()

if __name__ == "__main__":
    main()