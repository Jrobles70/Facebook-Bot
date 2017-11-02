from threading import Thread

def runMulti(active, action, length, interval, run, random):
    """
    :description: Creates a thread for each account to run on. I created a methods dict so I can have different accounts
                  perform different actions or tests all together.
    """
    password = "U0NetSec"

    threads = {}

    try:
        for key in active:
            # Signs accounts in and assigns them the method we want them to do
            threads[key] = Thread(target=action, args=(active[key], length, interval, run, random))

        for key in threads:
            # Starts each thread
            print("Creating thread for " + key)
            threads[key].start()

    except KeyboardInterrupt:
        end(active, threads)

def end(active, threads):
    for key in active:
        # Stops their current action
        active[key].finish()

    print("Done!")




