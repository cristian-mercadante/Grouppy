from app.models import Friend
from google.appengine.ext import deferred
from google.appengine.ext import ndb


def add_escludi_to_friend(value=False, cursor=None):
    batch_size = 10
    friends, next_cursor, is_there_more = Friend.query().fetch_page(batch_size, start_cursor=cursor)

    for f in friends:
        f.escludi = value

    if len(friends) > 0:
        ndb.put_multi(friends)

    if is_there_more:
        deferred.defer(add_escludi_to_friend, value=value, cursor=next_cursor)
