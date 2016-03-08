__author__ = 'renhao.cui'

import time
from TwitterSearch import *

recordFile = open("tweetData//SpeedStick", 'a')

c_k = 'NNFnQv3zyeM99IDXg1IOrtMcQ'
c_s = 'GDc4vZtorwOiPgDNiaGrWDTWfqKNW2ZzMOTUkpJuF7gLdBCLZI'
a_t = '141612471-AnWgHssHt5rtOhlC8Cmy6GwEge9Z81v8MHQw6nXr'
a_t_s = 'gNE1nOhhc5CJoinMR6eUuyYBLR8YT3wK0tRb4yTUAY8Od'

try:
    tso = TwitterSearchOrder()
    tso.set_keywords(['Speed Stick'])  # let's define all words we would like to have a look for
    tso.set_language('en')
    tso.set_count(100)  # 100 results per page
    tso.set_include_entities(True)  # give all those entity information

    size = 10
    for i in range(size):
        ts = TwitterSearch(consumer_key=c_k, consumer_secret=c_s, access_token=a_t, access_token_secret=a_t_s)
        print "Collecting Tweets..."
        for tweet in ts.search_tweets_iterable(tso):
            recordFile.write(('[%s]:[%s][%s][%s][%s]:^{^%s^}^:[%s][%s]' % (
                tweet['id'], tweet['user']['id'], tweet['user']['followers_count'], tweet['user']['favourites_count'],
                tweet['user']['statuses_count'], tweet['text'], tweet['retweet_count'],
                tweet['favorite_count'])).encode('ascii', 'ignore'))
            recordFile.write('\n')
        if i < (size - 1):
            print "Waiting for 15 minutes..."
            time.sleep(900)

except TwitterSearchException as e:  # take care of all those ugly errors if there are some
    print(e)

recordFile.close()