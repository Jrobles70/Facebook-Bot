# Facebook Bot

These scripts can automatically control facebook accounts to post status', share posts, comment on posts, like/react to posts, go to next page, refresh, and most importantly automatically create facebook accounts. Every account and action will be stored in a db file using sqlite3. Using the run script you can run as many accounts as you own like for a specific period of time waiting a specific or random amount of time after each action. I included a version I wrote that uses Facebook's graph api but I found it to not very useful for our purposes. When an account posts a status or comment it is completely random from this website](http://watchout4snakes.com/wo4snakes/random/randomsentence).

## Getting Started

### Prerequisites

* Python 3 or above
* Selenium
* Sqlite3
* PhantomJS.exe (Included in this folder)
* A Facebook account token and ID if using the API version ([Can be found here](https://developers.facebook.com/tools/explorer/))
* Pictures in the pics folder to use as captcha photos

### Installing

```
pip install selenium
pip install sqlite3
```

## Running the tests

To run the accounts add the following information into the command line:

```
Usage: run.py [OPTIONS]

Options:
  -l, --length INTEGER    set length to run
  -i, --interval INTEGER  set time in between each action. Use two numbers to
                          have a random interval between them
  -r, --run TEXT          runs a single action or actions for specific length
                          with a specific interval.
  -rand, --random         The order of the actions will be in random order
  -m, --multi INTEGER     number of accounts to use
  --help                  Show this message and exit.
  ```
### Note

* If you would like every interval to be a random number between two numbers enter two -i values (1st -i must be smaller than 2nd)
* To use all actions use -r all
* To use only specific actions enter an -r value for each one (Options: post, like, comment, share, next)
* User will be prompted to enter length and interval if not given (Does not support random intervals)
* User will be told if accounts are blocked due to suspicious activity and if there are not enough accounts signed in
* If no value is given when prompted the defaul amount will be used (number in [])

```
length in seconds. 0 to run once. [60]: 0
time between each action in seconds [5]: 
number of accounts to run [1]: 1
```

## Command Line Examples

### Running a single action once. User will be prompted to enter -r, -i and -m

```
python run.py -r post -l 0
...
```
OR

```
python run.py -r post
length in seconds. 0 to run once. [60]: 0
time between each action in seconds [5]: 
number of accounts to run [1]: 1
```


### Running all actions in order with a random wait time between 1 and 60 second intervals
```
python run.py -r all -i 1 -i 60
...
```

### Running all actions in random order for 20 minutes with 30 second intervals
```
python run.py -r all -rand -l 1200 -i 30
...
```
OR

```
python run.py -r all -rand
length in seconds. 0 to run once. [60]: 1200
time between each action in seconds [5]: 30
number of accounts to run [1]: 1
```

### Running all actions in random order across 3 accounts for 1 minute with 3 second intervals
```
python run.py -r all -rand -m 3
...
```
OR

```
python run.py -r all -rand
length in seconds. 0 to run once. [60]: 
time between each action in seconds [5]:
number of accounts to run [1]: 1
```

## Account Creation
 After a lot of testing I found that using ([a temporary email site](https://temp-mail.org/en/)) Facebook will occasionally ask for just an email verification. Facebook will eventually ask for a phone verification so the script will make note of that and move on to the next account. Account information will need to be added manually.
