__author__ = 'Mayank Tiwari'

import logging.config

from models.game import *

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
import datetime


class Post(Document):
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    author = StringField(required=True, max_length=50)
    published = DateTimeField(default=datetime.datetime.now)

    @queryset_manager
    def live_posts(clazz, queryset):
        return queryset.filter(published=not None)


if Post.objects.count() == 0:
    post_1 = Post(
        title='Sample Post',
        content='Some engaging content',
        author='Scott'
    )
    post_1.save()  # This will perform an insert
    print(post_1.title)
    post_1.title = 'A Better Post Title'
    post_1.save()  # This will perform an atomic edit on "title"
    print(post_1.title)

for post in Post.live_posts:
    print(post.author)
