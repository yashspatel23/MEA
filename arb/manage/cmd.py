from collections import OrderedDict
import datetime
import json
import os
import re
import time

import click
from elasticsearch.client import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import ipdb
import pytz

from arb.app.routes import application
from arb import bootstrap


@application.cli.command()
def setup():
    click.secho('Bootstrapping and setting up databases...', fg='green')
    bootstrap()
    click.secho('Done.', fg='green')



