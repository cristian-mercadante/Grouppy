# -*- coding: utf8 -*-
import os
from google.appengine.ext import vendor

vendor.add('lib')

if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    GAE_DEV = True
else:
    GAE_DEV = False
