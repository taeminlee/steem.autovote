#-*- coding: utf-8 -*-
from steem.blog import Blog
from steem import Steem
import io
import os.path
import json
import time
from functools import reduce

def load_config():
    config_path = 'voting_rule.json'
    with io.open(config_path, 'r') as fp:
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

def vote(postId, voter, weight=100):
    voter['s'].commit.vote(postId, weight, voter['id'])

def run_vote(userId, voter):
    p, p_raw = get_new_post(userId)
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
                rst = run_vote(userId, user)
                print("%s %s Ended"%(mode, userId))
                if rst != False:
                    print("VOTED POST : https://steemit.com/%s" % rst)
        print("COOLDOWN")
        time.sleep(60*cfg['refresh'])

if __name__ == "__main__":
    run()