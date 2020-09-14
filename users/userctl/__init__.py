#!/usr/bin/env python3

# Dependencies
# ============

# Standard
# --------
import argparse
import os
import sys
import json
import re
import random
import string
import codecs
from datetime import date

# Non-standard
# ------------
# See http://tinydb.readthedocs.io/
from tinydb import TinyDB, Query
from tinydb.storages import Storage, touch

# See https://www.dulwich.io/
from dulwich.repo import Repo
from dulwich.errors import NotGitRepository
import dulwich.porcelain as git

# See https://passlib.readthedocs.io/
import passlib.apps as pwd_context

# Utility definitions
# ===================
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


# Initializing
# ============

# Calculate defaults
# ------------------

default_users_file = os.path.join(os.getcwd(), 'db.json')

mscwg_email = 'mscwg@rda-groups.org'

db_format = {
    'indent': 1,
    'ensure_ascii': False
}

# Command-line arguments
# ----------------------
# We reuse the following help text a lot:
user_argument = {'help': 'openID/OAuth ID code of the user'}
apiuser_argument = {'help': 'user ID of the API user'}

# Here is the actual parser:
parser = argparse.ArgumentParser(
    prog='python3 -m userctl',
    description='Metadata Standards Catalog User Control Tool.'
                ' Registers new API users, and blocks/unblocks both API and'
                ' regular users.')
parser.add_argument(
    '-u',
    '--user-db', help='location of user database file (instance/users/db.json)',
    action='store',
    default=default_users_file,
    dest='userdb')
subparsers = parser.add_subparsers(
    title='subcommands',
    help='perform database operation')
parser_blockuser = subparsers.add_parser(
    'block-user',
    help='block regular user of the Catalog')
parser_blockuser.add_argument(
    'userid',
    **user_argument)
parser_blockapiuser = subparsers.add_parser(
    'block-api-user',
    help='block user of the restricted Catalog API')
parser_blockapiuser.add_argument(
    'userid',
    **apiuser_argument)
parser_unblockuser = subparsers.add_parser(
    'unblock-user',
    help='unblock regular user of the Catalog')
parser_unblockuser.add_argument(
    'userid',
    **user_argument)
parser_unblockapiuser = subparsers.add_parser(
    'unblock-api-user',
    help='unblock user of the restricted Catalog API')
parser_unblockapiuser.add_argument(
    'userid',
    **apiuser_argument)
parser_addapiuser = subparsers.add_parser(
    'add-api-user',
    help='add API user to user database')
parser_addapiuser.add_argument(
    'name',
    help='name of the API user')
parser_addapiuser.add_argument(
    'userid',
    **apiuser_argument)
parser_addapiuser.add_argument(
    'email',
    help='contact email address for the API user')


# Operations
# ==========
# Block user
# ----------
def dbBlock(args, api=False, toggle=True):
    """Blocks or unblocks user. If `api` is False, operates on regular Web
    user; if True, operates on API user. If `toggle` is True, blocks the user;
    if False, unblocks the user.
    """
    # Retrieve user record
    db = TinyDB((args.userdb), **db_format)
    User = Query()

    if api:
        table = db.table('api_users')
    else:
        table = db

    if toggle:
        verb = ('Block', 'Blocking', 'blocked')
    else:
        verb = ('Unblock', 'Unblocking', 'unblocked')

    user_list = table.search(User.userid == args.userid)
    status = len(user_list)
    if status < 1:
        print(f"User {args.userid} not found. Exiting.")
        sys.exit(1)
    elif status > 1:
        print('ID not unique. Is there a problem in the database?')
        sys.exit(2)

    print(f"{verb[1]} user {args.userid}...")
    user = user_list[0]

    # Update user record
    table.update({'blocked': toggle}, doc_ids=[user.doc_id])

    # Add file to Git index
    try:
        repo = Repo(os.path.dirname(args.userdb))
    except NotGitRepository:
        repo = Repo.init(os.path.dirname(args.userdb))

    git.add(repo=repo, paths=[args.userdb])

    # Prepare commit information
    committer = f"MSCWG <{mscwg_email}>".encode('utf8')
    author = committer
    message = (f"{verb[0]} user {args.userid}\n\nChanged by userctl"
               .encode('utf8'))

    # Execute commit
    git.commit(repo, message=message, author=author, committer=committer)
    print(f"User successfully {verb[2]}.")


def dbBlockApi(args):
    dbBlock(args, api=True)


def dbUnblock(args):
    dbBlock(args, toggle=False)


def dbUnblockApi(args):
    dbBlock(args, api=True, toggle=False)


parser_blockuser.set_defaults(func=dbBlock)
parser_blockapiuser.set_defaults(func=dbBlockApi)
parser_unblockuser.set_defaults(func=dbUnblock)
parser_unblockapiuser.set_defaults(func=dbUnblockApi)


# Add API user
# ------------
def dbAdd(args):
    db = TinyDB((args.userdb), **db_format)
    table = db.table('api_users')
    name = args.name
    userid = args.userid
    email = args.email

    # Validate user input...
    errors = list()
    badchars = set()
    # Check username:
    for char in userid:
        if char not in (string.ascii_letters + string.digits + '-_.'):
            badchars.add(char)
    if badchars:
        errors.append("These characters are not allowed in the user ID: "
                        f'''"{''.join(badchars)}"''')
    # Check email:
    if not re.match('[^@\\s]+@[^@\\s\\.]+\\.[^@\\s]+', email):
        errors.append('That email address does not look quite right.')
    # Were there errors?
    if errors:
        print('\n'.join(errors))
        sys.exit(1)

    # Generate pseudo-random string
    try:
        rng = random.SystemRandom()
    except NotImplementedError:
        rng = random
    password = ''.join(rng.choice(string.ascii_letters + string.digits)
                       for _ in range(12))

    # Update user record
    table.insert({
        'name': name,
        'email': email,
        'userid': userid,
        'password_hash': pwd_context.hash(password)})

    # Add file to Git index
    try:
        repo = Repo(os.path.dirname(args.userdb))
    except NotGitRepository:
        repo = Repo.init(os.path.dirname(args.userdb))
    git.add(repo=repo, paths=[args.userdb])

    # Prepare commit information
    committer = f"MSCWG <{mscwg_email}>".encode('utf8')
    author = committer
    message = (f"Add API user {name}\n\nChanged by userctl"
               .encode('utf8'))

    # Execute commit
    git.commit(repo, message=message, author=author, committer=committer)
    print(f"User successfully added with password {password}")


parser_addapiuser.set_defaults(func=dbAdd)


# Processing
# ==========
def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
