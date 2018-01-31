#-*- coding: utf-8 -*-
from steem.blog import Blog
from steem import Steem
import io
import os.path
import json
import time
import datetime
from functools import reduce
import codecs

def load_config():
    config_path = 'voting_rule.json'
    with codecs.open(config_path, encoding="UTF-8") as fp:
        return json.load(fp)

def login(user):
    user['s'] = Steem(keys=[user['postkey']])

def get_new_post(userId):
    b = Blog(userId)
    p = next(b)
    return p.export(), p

def get_identifier(post):
    return post['identifier']

def double_vote_check(post, user):
    return len(list(filter(lambda vote:vote['voter'] == user['id'],post['active_votes']))) > 0

def time_delay_check(post, rule):
    timediff = datetime.datetime.utcnow() - post['created']
    elapsed_minutes = timediff.seconds / 60
    return elapsed_minutes < rule['delay']

def vote(postId, voter, weight=100):
    voter['s'].commit.vote(postId, weight, voter['id'])

def get_title_body(post):
    return post['title'], post['body']

def universal(W, text):
    if len(W) == 0:
        return True # for whitelist check
    return reduce(lambda x,y:x&y,map(lambda w:w in text, W))

def existential(W, text):
    if (len(W) == 0):
        return False # for blacklist check
    return reduce(lambda x,y:x|y,map(lambda w:w in text, W))

def white_black_check(post,rule):
    t, b = get_title_body(post)
    white = universal(rule['title_white'],t) & universal(rule['body_white'],b)
    black = existential(rule['title_black'],t) | existential(rule['body_black'],b)
    return white and not black

def run_vote(rule, voter):
    p, p_raw = get_new_post(rule['id'])
    if(white_black_check(p,rule) == False):
        return False
    if(time_delay_check(p,rule)):
        return False
    if(double_vote_check(p,voter)):
        return False
    postId = get_identifier(p)
    vote(postId, voter, voter['weight'])
    return postId

def run():
    cfg = load_config()
    user = cfg['user']
    print("LOGIN")    
    login(user)
    while True:
        for rule in cfg['rule']:
            userId = rule['id']
            mode = rule['mode']
            print("%s %s"%(mode, userId))
            if(mode == 'vote'):
                rst = run_vote(rule, user)
                print("%s %s Ended"%(mode, userId))
                if rst != False:
                    print("VOTED POST : https://steemit.com/%s" % rst)
        print("COOLDOWN")
        time.sleep(60*cfg['refresh'])

if __name__ == "__main__":
    run()