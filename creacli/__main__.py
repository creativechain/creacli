#!/usr/bin/env python3

import sys
import os
import argparse
import json
import re
from pprint import pprint
from creapybase.account import PrivateKey, PublicKey, Address
import creapybase.transactions as transactions
from creapy.storage import configStorage as config
from creapy.utils import (
    resolveIdentifier,
    yaml_parse_file,
    formatTime,
    strfage,
)
from creapy.crea import Crea
from creapy.amount import Amount
from creapy.account import Account
from creapy.post import Post
from creapy.blockchain import Blockchain
from creapy.block import Block
from creapy.dex import Dex
from creapy.witness import Witness
import frontmatter
import time
from prettytable import PrettyTable
import logging
from .ui import (
    dump_recursive_parents,
    dump_recursive_comments,
    list_posts,
    markdownify,
    format_operation_details,
    confirm,
    print_permissions,
    get_terminal
)
from creapy.exceptions import AccountDoesNotExistsException
import pkg_resources  # part of setuptools


availableConfigurationKeys = [
    "default_author",
    "default_voter",
    "default_account",
    "node",
    "rpcuser",
    "rpcpassword",
    "default_vote_weight",
    "list_sorting",
    "categories_sorting",
    "limit",
    "post_category",
]


def main():
    global args

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Command line tool to interact with the Crea network"
    )

    """
        Default settings for all tools
    """
    parser.add_argument(
        '--node',
        type=str,
        default=config["node"],
        help='Websocket URL for public Crea API (default: "wss://cread.creas.io/")'
    )
    parser.add_argument(
        '--rpcuser',
        type=str,
        default=config["rpcuser"],
        help='Websocket user if authentication is required'
    )
    parser.add_argument(
        '--rpcpassword',
        type=str,
        default=config["rpcpassword"],
        help='Websocket password if authentication is required'
    )
    parser.add_argument(
        '--nobroadcast', '-d',
        action='store_true',
        help='Do not broadcast anything'
    )
    parser.add_argument(
        '--nowallet', '-p',
        action='store_true',
        help='Do not load the wallet'
    )
    parser.add_argument(
        '--unsigned', '-x',
        action='store_true',
        help='Do not try to sign the transaction'
    )
    parser.add_argument(
        '--expires', '-e',
        default=30,
        help='Expiration time in seconds (defaults to 30)'
    )
    parser.add_argument(
        '--verbose', '-v',
        type=int,
        default=3,
        help='Verbosity'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {version}'.format(
            version=pkg_resources.require("creacli")[0].version
        )
    )

    subparsers = parser.add_subparsers(help='sub-command help')

    """
        Command "set"
    """
    setconfig = subparsers.add_parser('set', help='Set configuration')
    setconfig.add_argument(
        'key',
        type=str,
        choices=availableConfigurationKeys,
        help='Configuration key'
    )
    setconfig.add_argument(
        'value',
        type=str,
        help='Configuration value'
    )
    setconfig.set_defaults(command="set")

    """
        Command "config"
    """
    configconfig = subparsers.add_parser('config', help='Show local configuration')
    configconfig.set_defaults(command="config")

    """
        Command "info"
    """
    parser_info = subparsers.add_parser('info', help='Show infos about CreaPy and Crea')
    parser_info.set_defaults(command="info")
    parser_info.add_argument(
        'objects',
        nargs='*',
        type=str,
        help='General information about the blockchain, a block, an account name, a post, a public key, ...'
    )

    """
        Command "changewalletpassphrase"
    """
    changepasswordconfig = subparsers.add_parser('changewalletpassphrase', help='Change wallet password')
    changepasswordconfig.set_defaults(command="changewalletpassphrase")

    """
        Command "addkey"
    """
    addkey = subparsers.add_parser('addkey', help='Add a new key to the wallet')
    addkey.add_argument(
        '--unsafe-import-key',
        nargs='*',
        type=str,
        help='private key to import into the wallet (unsafe, unless you delete your bash history)'
    )
    addkey.set_defaults(command="addkey")

    """
        Command "delkey"
    """
    delkey = subparsers.add_parser('delkey', help='Delete keys from the wallet')
    delkey.add_argument(
        'pub',
        nargs='*',
        type=str,
        help='the public key to delete from the wallet'
    )
    delkey.set_defaults(command="delkey")

    """
        Command "getkey"
    """
    getkey = subparsers.add_parser('getkey', help='Dump the privatekey of a pubkey from the wallet')
    getkey.add_argument(
        'pub',
        type=str,
        help='the public key for which to show the private key'
    )
    getkey.set_defaults(command="getkey")

    """
        Command "listkeys"
    """
    listkeys = subparsers.add_parser('listkeys', help='List available keys in your wallet')
    listkeys.set_defaults(command="listkeys")

    """
        Command "listaccounts"
    """
    listaccounts = subparsers.add_parser('listaccounts', help='List available accounts in your wallet')
    listaccounts.set_defaults(command="listaccounts")

    """
        Command "list"
    """
    parser_list = subparsers.add_parser('list', help='List posts on Crea')
    parser_list.set_defaults(command="list")
    parser_list.add_argument(
        '--start',
        type=str,
        help='Start list from this identifier (pagination)'
    )
    parser_list.add_argument(
        '--category',
        type=str,
        help='Only posts with in this category'
    )
    parser_list.add_argument(
        '--sort',
        type=str,
        default=config["list_sorting"],
        choices=["trending", "created", "active", "cashout", "payout", "votes", "children", "hot"],
        help='Sort posts'
    )
    parser_list.add_argument(
        '--limit',
        type=int,
        default=config["limit"],
        help='Limit posts by number'
    )
    parser_list.add_argument(
        '--columns',
        type=str,
        nargs="+",
        help='Display custom columns'
    )

    """
        Command "categories"
    """
    parser_categories = subparsers.add_parser('categories', help='Show categories')
    parser_categories.set_defaults(command="categories")
    parser_categories.add_argument(
        '--sort',
        type=str,
        default=config["categories_sorting"],
        choices=["trending", "best", "active", "recent"],
        help='Sort categories'
    )
    parser_categories.add_argument(
        'category',
        nargs="?",
        type=str,
        help='Only categories used by this author'
    )
    parser_categories.add_argument(
        '--limit',
        type=int,
        default=config["limit"],
        help='Limit categories by number'
    )

    """
        Command "read"
    """
    parser_read = subparsers.add_parser('read', help='Read a post on Crea')
    parser_read.set_defaults(command="read")
    parser_read.add_argument(
        'post',
        type=str,
        help='@author/permlink-identifier of the post to read (e.g. @jared/crea-python)'
    )
    parser_read.add_argument(
        '--full',
        action='store_true',
        help='Show full header information (YAML formated)'
    )
    parser_read.add_argument(
        '--comments',
        action='store_true',
        help='Also show all comments'
    )
    parser_read.add_argument(
        '--parents',
        type=int,
        default=0,
        help='Show x parents for the reply'
    )
    parser_read.add_argument(
        '--format',
        type=str,
        default=config["format"],
        help='Format post',
        choices=["markdown", "raw"],
    )

    """
        Command "post"
    """
    parser_post = subparsers.add_parser('post', help='Post something new')
    parser_post.set_defaults(command="post")
    parser_post.add_argument(
        '--author',
        type=str,
        required=False,
        default=config["default_author"],
        help='Publish post as this user (requires to have the key installed in the wallet)'
    )
    parser_post.add_argument(
        '--permlink',
        type=str,
        required=False,
        help='The permlink (together with the author identifies the post uniquely)'
    )
    parser_post.add_argument(
        '--category',
        default=config["post_category"],
        type=str,
        help='Specify category'
    )
    parser_post.add_argument(
        '--tags',
        default=[],
        help='Specify tags',
        nargs='*',
    )
    parser_post.add_argument(
        '--title',
        type=str,
        required=False,
        help='Title of the post'
    )
    parser_post.add_argument(
        '--file',
        type=str,
        default=None,
        help='Filename to open. If not present, or "-", stdin will be used'
    )

    """
        Command "reply"
    """
    reply = subparsers.add_parser('reply', help='Reply to an existing post')
    reply.set_defaults(command="reply")
    reply.add_argument(
        'replyto',
        type=str,
        help='@author/permlink-identifier of the post to reply to (e.g. @jared/crea-python)'
    )
    reply.add_argument(
        '--author',
        type=str,
        required=False,
        default=config["default_author"],
        help='Publish post as this user (requires to have the key installed in the wallet)'
    )
    reply.add_argument(
        '--permlink',
        type=str,
        required=False,
        help='The permlink (together with the author identifies the post uniquely)'
    )
    reply.add_argument(
        '--title',
        type=str,
        required=False,
        help='Title of the post'
    )
    reply.add_argument(
        '--file',
        type=str,
        required=False,
        help='Send file as responds. If "-", read from stdin'
    )

    """
        Command "edit"
    """
    parser_edit = subparsers.add_parser('edit', help='Edit to an existing post')
    parser_edit.set_defaults(command="edit")
    parser_edit.add_argument(
        'post',
        type=str,
        help='@author/permlink-identifier of the post to edit to (e.g. @jared/crea-python)'
    )
    parser_edit.add_argument(
        '--author',
        type=str,
        required=False,
        default=config["default_author"],
        help='Post an edit as another author'
    )
    parser_edit.add_argument(
        '--file',
        type=str,
        required=False,
        help='Patch with content of this file'
    )
    parser_edit.add_argument(
        '--replace',
        action='store_true',
        help="Don't patch but replace original post (will make you lose votes)"
    )

    """
        Command "upvote"
    """
    parser_upvote = subparsers.add_parser('upvote', help='Upvote a post')
    parser_upvote.set_defaults(command="upvote")
    parser_upvote.add_argument(
        'post',
        type=str,
        help='@author/permlink-identifier of the post to upvote to (e.g. @jared/crea-python)'
    )
    parser_upvote.add_argument(
        '--voter',
        type=str,
        required=False,
        default=config["default_voter"],
        help='The voter account name'
    )
    parser_upvote.add_argument(
        '--weight',
        type=float,
        default=config["default_vote_weight"],
        required=False,
        help='Actual weight (from 0.1 to 100.0)'
    )

    """
        Command "downvote"
    """
    parser_downvote = subparsers.add_parser('downvote', help='Downvote a post')
    parser_downvote.set_defaults(command="downvote")
    parser_downvote.add_argument(
        '--voter',
        type=str,
        default=config["default_voter"],
        help='The voter account name'
    )
    parser_downvote.add_argument(
        'post',
        type=str,
        help='@author/permlink-identifier of the post to downvote to (e.g. @jared/crea-python)'
    )
    parser_downvote.add_argument(
        '--weight',
        type=float,
        default=config["default_vote_weight"],
        required=False,
        help='Actual weight (from 0.1 to 100.0)'
    )

    """
        Command "replies"
    """
    replies = subparsers.add_parser('replies', help='Show recent replies to your posts')
    replies.set_defaults(command="replies")
    replies.add_argument(
        '--author',
        type=str,
        required=False,
        default=config["default_author"],
        help='Show replies to this author'
    )
    replies.add_argument(
        '--limit',
        type=int,
        default=config["limit"],
        help='Limit posts by number'
    )

    """
        Command "transfer"
    """
    parser_transfer = subparsers.add_parser('transfer', help='Transfer CREA')
    parser_transfer.set_defaults(command="transfer")
    parser_transfer.add_argument(
        'to',
        type=str,
        help='Recepient'
    )
    parser_transfer.add_argument(
        'amount',
        type=float,
        help='Amount to transfer'
    )
    parser_transfer.add_argument(
        'asset',
        type=str,
        choices=["CREA", "CBD", "BET", "TBD"],
        help='Asset to transfer (i.e. CREA or CBD)'
    )
    parser_transfer.add_argument(
        'memo',
        type=str,
        nargs="?",
        default="",
        help='Optional memo'
    )
    parser_transfer.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Transfer from this account'
    )

    """
        Command "powerup"
    """
    parser_powerup = subparsers.add_parser('powerup', help='Power up (vest CREA as CREA POWER)')
    parser_powerup.set_defaults(command="powerup")
    parser_powerup.add_argument(
        'amount',
        type=str,
        help='Amount of VESTS to powerup'
    )
    parser_powerup.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Powerup from this account'
    )
    parser_powerup.add_argument(
        '--to',
        type=str,
        required=False,
        default=None,
        help='Powerup this account'
    )

    """
        Command "powerdown"
    """
    parser_powerdown = subparsers.add_parser('powerdown', help='Power down (start withdrawing CREA from CREA POWER)')
    parser_powerdown.set_defaults(command="powerdown")
    parser_powerdown.add_argument(
        'amount',
        type=str,
        help='Amount of VESTS to powerdown'
    )
    parser_powerdown.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='powerdown from this account'
    )

    """
        Command "powerdownroute"
    """
    parser_powerdownroute = subparsers.add_parser('powerdownroute', help='Setup a powerdown route')
    parser_powerdownroute.set_defaults(command="powerdownroute")
    parser_powerdownroute.add_argument(
        'to',
        type=str,
        default=config["default_author"],
        help='The account receiving either VESTS/BexPower or CREA.'
    )
    parser_powerdownroute.add_argument(
        '--percentage',
        type=float,
        default=100,
        help='The percent of the withdraw to go to the "to" account'
    )
    parser_powerdownroute.add_argument(
        '--account',
        type=str,
        default=config["default_author"],
        help='The account which is powering down'
    )
    parser_powerdownroute.add_argument(
        '--auto_vest',
        action='store_true',
        help=('Set to true if the from account should receive the VESTS as'
              'VESTS, or false if it should receive them as CREA.')
    )

    """
        Command "convert"
    """
    parser_convert = subparsers.add_parser('convert', help='Convert CREA Dollars to CREA (takes a week to settle)')
    parser_convert.set_defaults(command="convert")
    parser_convert.add_argument(
        'amount',
        type=float,
        help='Amount of CBD to convert'
    )
    parser_convert.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Convert from this account'
    )

    """
        Command "balance"
    """
    parser_balance = subparsers.add_parser('balance', help='Show the balance of one more more accounts')
    parser_balance.set_defaults(command="balance")
    parser_balance.add_argument(
        'account',
        type=str,
        nargs="*",
        default=config["default_author"],
        help='balance of these account (multiple accounts allowed)'
    )

    """
        Command "history"
    """
    parser_history = subparsers.add_parser('history', help='Show the history of an account')
    parser_history.set_defaults(command="history")
    parser_history.add_argument(
        'account',
        type=str,
        nargs="?",
        default=config["default_author"],
        help='History of this account'
    )
    parser_history.add_argument(
        '--limit',
        type=int,
        default=config["limit"],
        help='Limit number of entries'
    )
    parser_history.add_argument(
        '--memos',
        action='store_true',
        help='Show (decode) memos'
    )
    parser_history.add_argument(
        '--csv',
        action='store_true',
        help='Output in CSV format'
    )
    parser_history.add_argument(
        '--first',
        type=int,
        default=99999999999999,
        help='Transaction number (#) of the last transaction to show.'
    )
    parser_history.add_argument(
        '--types',
        type=str,
        nargs="*",
        default=[],
        help='Show only these operation types'
    )
    parser_history.add_argument(
        '--exclude_types',
        type=str,
        nargs="*",
        default=[],
        help='Do not show operations of this type'
    )

    """
        Command "interest"
    """
    interest = subparsers.add_parser('interest', help='Get information about interest payment')
    interest.set_defaults(command="interest")
    interest.add_argument(
        'account',
        type=str,
        nargs="*",
        default=config["default_author"],
        help='Inspect these accounts'
    )

    """
        Command "permissions"
    """
    parser_permissions = subparsers.add_parser('permissions', help='Show permissions of an account')
    parser_permissions.set_defaults(command="permissions")
    parser_permissions.add_argument(
        'account',
        type=str,
        nargs="?",
        default=config["default_author"],
        help='Account to show permissions for'
    )

    """
        Command "allow"
    """
    parser_allow = subparsers.add_parser('allow', help='Allow an account/key to interact with your account')
    parser_allow.set_defaults(command="allow")
    parser_allow.add_argument(
        '--account',
        type=str,
        nargs="?",
        default=config["default_author"],
        help='The account to allow action for'
    )
    parser_allow.add_argument(
        'foreign_account',
        type=str,
        nargs="?",
        help='The account or key that will be allowed to interact as your account'
    )
    parser_allow.add_argument(
        '--permission',
        type=str,
        default="posting",
        choices=["owner", "posting", "active"],
        help=('The permission to grant (defaults to "posting")')
    )
    parser_allow.add_argument(
        '--weight',
        type=int,
        default=None,
        help=('The weight to use instead of the (full) threshold. '
              'If the weight is smaller than the threshold, '
              'additional signatures are required')
    )
    parser_allow.add_argument(
        '--threshold',
        type=int,
        default=None,
        help=('The permission\'s threshold that needs to be reached '
              'by signatures to be able to interact')
    )

    """
        Command "disallow"
    """
    parser_disallow = subparsers.add_parser('disallow', help='Remove allowance an account/key to interact with your account')
    parser_disallow.set_defaults(command="disallow")
    parser_disallow.add_argument(
        '--account',
        type=str,
        nargs="?",
        default=config["default_author"],
        help='The account to disallow action for'
    )
    parser_disallow.add_argument(
        'foreign_account',
        type=str,
        help='The account or key whose allowance to interact as your account will be removed'
    )
    parser_disallow.add_argument(
        '--permission',
        type=str,
        default="posting",
        choices=["owner", "posting", "active"],
        help=('The permission to remove (defaults to "posting")')
    )
    parser_disallow.add_argument(
        '--threshold',
        type=int,
        default=None,
        help=('The permission\'s threshold that needs to be reached '
              'by signatures to be able to interact')
    )

    """
        Command "newaccount"
    """
    parser_newaccount = subparsers.add_parser('newaccount', help='Create a new account')
    parser_newaccount.set_defaults(command="newaccount")
    parser_newaccount.add_argument(
        'accountname',
        type=str,
        help='New account name'
    )
    parser_newaccount.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Account that pays the fee'
    )

    """
        Command "importaccount"
    """
    parser_importaccount = subparsers.add_parser('importaccount', help='Import an account using a passphrase')
    parser_importaccount.set_defaults(command="importaccount")
    parser_importaccount.add_argument(
        'account',
        type=str,
        help='Account name'
    )
    parser_importaccount.add_argument(
        '--roles',
        type=str,
        nargs="*",
        default=["active", "posting", "memo"],  # no owner
        help='Import specified keys (owner, active, posting, memo)'
    )

    """
        Command "updateMemoKey"
    """
    parser_updateMemoKey = subparsers.add_parser('updatememokey', help='Update an account\'s memo key')
    parser_updateMemoKey.set_defaults(command="updatememokey")
    parser_updateMemoKey.add_argument(
        '--account',
        type=str,
        nargs="?",
        default=config["default_author"],
        help='The account to updateMemoKey action for'
    )
    parser_updateMemoKey.add_argument(
        '--key',
        type=str,
        default=None,
        help='The new memo key'
    )

    """
        Command "approvewitness"
    """
    parser_approvewitness = subparsers.add_parser('approvewitness', help='Approve a witnesses')
    parser_approvewitness.set_defaults(command="approvewitness")
    parser_approvewitness.add_argument(
        'witness',
        type=str,
        help='Witness to approve'
    )
    parser_approvewitness.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Your account'
    )

    """
        Command "disapprovewitness"
    """
    parser_disapprovewitness = subparsers.add_parser('disapprovewitness', help='Disapprove a witnesses')
    parser_disapprovewitness.set_defaults(command="disapprovewitness")
    parser_disapprovewitness.add_argument(
        'witness',
        type=str,
        help='Witness to disapprove'
    )
    parser_disapprovewitness.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Your account'
    )

    """
        Command "sign"
    """
    parser_sign = subparsers.add_parser('sign', help='Sign a provided transaction with available and required keys')
    parser_sign.set_defaults(command="sign")
    parser_sign.add_argument(
        '--file',
        type=str,
        required=False,
        help='Load transaction from file. If "-", read from stdin (defaults to "-")'
    )

    """
        Command "broadcast"
    """
    parser_broadcast = subparsers.add_parser('broadcast', help='broadcast a signed transaction')
    parser_broadcast.set_defaults(command="broadcast")
    parser_broadcast.add_argument(
        '--file',
        type=str,
        required=False,
        help='Load transaction from file. If "-", read from stdin (defaults to "-")'
    )

    """
        Command "orderbook"
    """
    orderbook = subparsers.add_parser('orderbook', help='Obtain orderbook of the internal market')
    orderbook.set_defaults(command="orderbook")
    orderbook.add_argument(
        '--chart',
        action='store_true',
        help="Enable charting (requires matplotlib)"
    )

    """
        Command "buy"
    """
    parser_buy = subparsers.add_parser('buy', help='Buy CREA or CBD from the internal market')
    parser_buy.set_defaults(command="buy")
    parser_buy.add_argument(
        'amount',
        type=float,
        help='Amount to buy'
    )
    parser_buy.add_argument(
        'asset',
        type=str,
        choices=["CREA", "CBD", "GOLOS", "GBG"],
        help='Asset to buy (i.e. CREA or SDB)'
    )
    parser_buy.add_argument(
        'price',
        type=float,
        help='Limit buy price denoted in (CBD per CREA)'
    )
    parser_buy.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_account"],
        help='Buy with this account (defaults to "default_account")'
    )

    """
        Command "sell"
    """
    parser_sell = subparsers.add_parser('sell', help='Sell CREA or CBD from the internal market')
    parser_sell.set_defaults(command="sell")
    parser_sell.add_argument(
        'amount',
        type=float,
        help='Amount to sell'
    )
    parser_sell.add_argument(
        'asset',
        type=str,
        choices=["CREA", "CBD", "BET", "TBD"],
        help='Asset to sell (i.e. CREA or CBD)'
    )
    parser_sell.add_argument(
        'price',
        type=float,
        help='Limit sell price denoted in (CBD per CREA)'
    )
    parser_sell.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_account"],
        help='Sell from this account (defaults to "default_account")'
    )
    """
        Command "cancel"
    """
    parser_cancel = subparsers.add_parser('cancel', help='Cancel order in the internal market')
    parser_cancel.set_defaults(command="cancel")
    parser_cancel.add_argument(
        'orderid',
        type=int,
        help='Orderid'
    )
    parser_cancel.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_account"],
        help='Cancel from this account (defaults to "default_account")'
    )

    """
        Command "repost"
    """
    parser_repost = subparsers.add_parser('repost', help='Repost an existing post')
    parser_repost.set_defaults(command="repost")
    parser_repost.add_argument(
        'identifier',
        type=str,
        help='@author/permlink-identifier of the post to repost'
    )
    parser_repost.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='Repost as this user (requires to have the key installed in the wallet)'
    )

    """
        Command "follow"
    """
    parser_follow = subparsers.add_parser('follow', help='Follow another account')
    parser_follow.set_defaults(command="follow")
    parser_follow.add_argument(
        'follow',
        type=str,
        help='Account to follow'
    )
    parser_follow.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_account"],
        help='Follow from this account'
    )
    parser_follow.add_argument(
        '--what',
        type=str,
        required=False,
        nargs="*",
        default=["blog"],
        help='Follow these objects (defaults to "blog")'
    )

    """
        Command "unfollow"
    """
    parser_unfollow = subparsers.add_parser('unfollow', help='unfollow another account')
    parser_unfollow.set_defaults(command="unfollow")
    parser_unfollow.add_argument(
        'unfollow',
        type=str,
        help='Account to unfollow'
    )
    parser_unfollow.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_account"],
        help='Unfollow from this account'
    )
    parser_unfollow.add_argument(
        '--what',
        type=str,
        required=False,
        nargs="*",
        default=[],
        help='Unfollow these objects (defaults to "blog")'
    )

    """
        Command "setprofile"
    """
    parser_setprofile = subparsers.add_parser('setprofile', help='Set a variable in an account\'s profile')
    parser_setprofile.set_defaults(command="setprofile")
    parser_setprofile.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='setprofile as this user (requires to have the key installed in the wallet)'
    )
    parser_setprofileA = parser_setprofile.add_argument_group('Multiple keys at once')
    parser_setprofileA.add_argument(
        '--pair',
        type=str,
        nargs='*',
        help='"Key=Value" pairs'
    )
    parser_setprofileB = parser_setprofile.add_argument_group('Just a single key')
    parser_setprofileB.add_argument(
        'variable',
        type=str,
        nargs='?',
        help='Variable to set'
    )
    parser_setprofileB.add_argument(
        'value',
        type=str,
        nargs='?',
        help='Value to set'
    )

    """
        Command "delprofile"
    """
    parser_delprofile = subparsers.add_parser('delprofile', help='Set a variable in an account\'s profile')
    parser_delprofile.set_defaults(command="delprofile")
    parser_delprofile.add_argument(
        '--account',
        type=str,
        required=False,
        default=config["default_author"],
        help='delprofile as this user (requires to have the key installed in the wallet)'
    )
    parser_delprofile.add_argument(
        'variable',
        type=str,
        nargs='*',
        help='Variable to set'
    )

    """
        Command "witnessupdate"
    """
    parser_witnessprops = subparsers.add_parser('witnessupdate', help='Change witness properties')
    parser_witnessprops.set_defaults(command="witnessupdate")
    parser_witnessprops.add_argument(
        '--witness',
        type=str,
        default=config["default_account"],
        help='Witness name'
    )
    parser_witnessprops.add_argument(
        '--maximum_block_size',
        type=float,
        required=False,
        help='Max block size'
    )
    parser_witnessprops.add_argument(
        '--account_creation_fee',
        type=float,
        required=False,
        help='Account creation fee'
    )
    parser_witnessprops.add_argument(
        '--cbd_interest_rate',
        type=float,
        required=False,
        help='CBD interest rate in percent'
    )
    parser_witnessprops.add_argument(
        '--url',
        type=str,
        required=False,
        help='Witness URL'
    )
    parser_witnessprops.add_argument(
        '--signing_key',
        type=str,
        required=False,
        help='Signing Key'
    )

    """
        Command "witnesscreate"
    """
    parser_witnesscreate = subparsers.add_parser('witnesscreate', help='Create a witness')
    parser_witnesscreate.set_defaults(command="witnesscreate")
    parser_witnesscreate.add_argument(
        'witness',
        type=str,
        help='Witness name'
    )
    parser_witnesscreate.add_argument(
        'signing_key',
        type=str,
        help='Signing Key'
    )
    parser_witnesscreate.add_argument(
        '--maximum_block_size',
        type=float,
        default="65536",
        help='Max block size'
    )
    parser_witnesscreate.add_argument(
        '--account_creation_fee',
        type=float,
        default=30,
        help='Account creation fee'
    )
    parser_witnesscreate.add_argument(
        '--cbd_interest_rate',
        type=float,
        default=0.0,
        help='CBD interest rate in percent'
    )
    parser_witnesscreate.add_argument(
        '--url',
        type=str,
        default="",
        help='Witness URL'
    )

    """
        Parse Arguments
    """
    args = parser.parse_args()

    # Logging
    log = logging.getLogger(__name__)
    verbosity = ["critical",
                 "error",
                 "warn",
                 "info",
                 "debug"][int(min(args.verbose, 4))]
    log.setLevel(getattr(logging, verbosity.upper()))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, verbosity.upper()))
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # GrapheneAPI logging
    if args.verbose > 4:
        verbosity = ["critical",
                     "error",
                     "warn",
                     "info",
                     "debug"][int(min((args.verbose - 4), 4))]
        gphlog = logging.getLogger("graphenebase")
        gphlog.setLevel(getattr(logging, verbosity.upper()))
        gphlog.addHandler(ch)
    if args.verbose > 8:
        verbosity = ["critical",
                     "error",
                     "warn",
                     "info",
                     "debug"][int(min((args.verbose - 8), 4))]
        gphlog = logging.getLogger("grapheneapi")
        gphlog.setLevel(getattr(logging, verbosity.upper()))
        gphlog.addHandler(ch)

    if not hasattr(args, "command"):
        parser.print_help()
        sys.exit(2)

    # We don't require RPC for these commands
    rpc_not_required = [
        "set",
        "config",
        ""]
    if args.command not in rpc_not_required and args.command:
        options = {
            "node": args.node,
            "rpcuser": args.rpcuser,
            "rpcpassword": args.rpcpassword,
            "nobroadcast": args.nobroadcast,
            "unsigned": args.unsigned,
            "expires": args.expires
        }

        # preload wallet with empty keys
        if args.nowallet:
            options.update({"wif": []})

        # Signing only requires the wallet, no connection
        # essential for offline/coldstorage signing
        if args.command == "sign":
            options.update({"offline": True})

        crea = Crea(**options)

    if args.command == "set":
        if (args.key in ["default_author",
                         "default_voter",
                         "default_account"] and
                args.value[0] == "@"):
            args.value = args.value[1:]
        config[args.key] = args.value

    elif args.command == "config":
        t = PrettyTable(["Key", "Value"])
        t.align = "l"
        for key in config:
            if key in availableConfigurationKeys:  # hide internal config data
                t.add_row([key, config[key]])
        print(t)

    elif args.command == "info":
        if not args.objects:
            t = PrettyTable(["Key", "Value"])
            t.align = "l"
            blockchain = Blockchain(mode="head")
            info = blockchain.info()
            median_price = crea.rpc.get_current_median_history_price()
            crea_per_mvest = (
                Amount(info["total_vesting_fund_crea"]).amount /
                (Amount(info["total_vesting_shares"]).amount / 1e6)
            )
            price = (
                Amount(median_price["base"]).amount /
                Amount(median_price["quote"]).amount
            )
            for key in info:
                t.add_row([key, info[key]])
            t.add_row(["CREA per mvest", crea_per_mvest])
            t.add_row(["internal price", price])
            print(t.get_string(sortby="Key"))

        for obj in args.objects:
            # Block
            if re.match("^[0-9]*$", obj):
                block = Block(obj)
                if block:
                    t = PrettyTable(["Key", "Value"])
                    t.align = "l"
                    for key in sorted(block):
                        value = block[key]
                        if key == "transactions":
                            value = json.dumps(value, indent=4)
                        t.add_row([key, value])
                    print(t)
                else:
                    print("Block number %s unknown" % obj)
            # Account name
            elif re.match("^[a-zA-Z0-9\-\._]{2,16}$", obj):
                from math import log10
                account = Account(obj)
                t = PrettyTable(["Key", "Value"])
                t.align = "l"
                for key in sorted(account):
                    value = account[key]
                    if (key == "json_metadata"):
                        value = json.dumps(
                            json.loads(value or "{}"),
                            indent=4
                        )
                    if key in ["posting",
                               "witness_votes",
                               "active",
                               "owner"]:
                        value = json.dumps(value, indent=4)
                    if key == "reputation" and int(value) > 0:
                        value = int(value)
                        rep = (max(log10(value) - 9, 0) * 9 + 25 if value > 0
                               else max(log10(-value) - 9, 0) * -9 + 25)
                        value = "{:.2f} ({:d})".format(
                            rep, value
                        )
                    t.add_row([key, value])
                print(t)

                # witness available?
                try:
                    witness = Witness(obj)
                    t = PrettyTable(["Key", "Value"])
                    t.align = "l"
                    for key in sorted(witness):
                        value = witness[key]
                        if key in ["props",
                                   "cbd_exchange_rate"]:
                            value = json.dumps(value, indent=4)
                        t.add_row([key, value])
                    print(t)
                except:
                    pass
            # Public Key
            elif re.match("^DWB.{48,55}$", obj):
                account = crea.wallet.getAccountFromPublicKey(obj)
                if account:
                    t = PrettyTable(["Account"])
                    t.align = "l"
                    t.add_row([account])
                    print(t)
                else:
                    print("Public Key not known" % obj)
            # Post identifier
            elif re.match(".*@.{3,16}/.*$", obj):
                post = Post(obj)
                if post:
                    t = PrettyTable(["Key", "Value"])
                    t.align = "l"
                    for key in sorted(post):
                        value = post[key]
                        if (key in ["tags",
                                    "json_metadata",
                                    "active_votes"
                                    ]):
                            value = json.dumps(value, indent=4)
                        t.add_row([key, value])
                    print(t)
                else:
                    print("Post now known" % obj)
            else:
                print("Couldn't identify object to read")

    elif args.command == "changewalletpassphrase":
        crea.wallet.changePassphrase()

    elif args.command == "addkey":
        if args.unsafe_import_key:
            for key in args.unsafe_import_key:
                try:
                    crea.wallet.addPrivateKey(key)
                except Exception as e:
                    print(str(e))
        else:
            import getpass
            while True:
                wifkey = getpass.getpass('Private Key (wif) [Enter to quit]:')
                if not wifkey:
                    break
                try:
                    crea.wallet.addPrivateKey(wifkey)
                except Exception as e:
                    print(str(e))
                    continue

                installedKeys = crea.wallet.getPublicKeys()
                if len(installedKeys) == 1:
                    name = crea.wallet.getAccountFromPublicKey(installedKeys[0])
                    print("=" * 30)
                    print("Setting new default user: %s" % name)
                    print()
                    print("You can change these settings with:")
                    print("    CreaPy set default_author <account>")
                    print("    CreaPy set default_voter <account>")
                    print("    CreaPy set default_account <account>")
                    print("=" * 30)
                    config["default_author"] = name
                    config["default_voter"] = name
                    config["default_account"] = name

    elif args.command == "delkey":
        if confirm(
            "Are you sure you want to delete keys from your wallet?\n"
            "This step is IRREVERSIBLE! If you don't have a backup, "
            "You may lose access to your account!"
        ):
            for pub in args.pub:
                crea.wallet.removePrivateKeyFromPublicKey(pub)

    elif args.command == "getkey":
        print(crea.wallet.getPrivateKeyForPublicKey(args.pub))

    elif args.command == "listkeys":
        t = PrettyTable(["Available Key"])
        t.align = "l"
        for key in crea.wallet.getPublicKeys():
            t.add_row([key])
        print(t)

    elif args.command == "listaccounts":
        t = PrettyTable(["Name", "Type", "Available Key"])
        t.align = "l"
        for account in crea.wallet.getAccounts():
            t.add_row([
                account["name"] or "n/a",
                account["type"] or "n/a",
                account["pubkey"]
            ])
        print(t)

    elif args.command == "reply":
        from textwrap import indent
        parent = crea.get_content(args.replyto)
        if parent["id"] == "0.0.0":
            print("Can't find post %s" % args.replyto)
            return

        reply_message = indent(parent["body"], "> ")

        post = frontmatter.Post(reply_message, **{
            "title": args.title if args.title else "Re: " + parent["title"],
            "author": args.author if args.author else "required",
            "replyto": args.replyto,
        })

        meta, json_meta, message = yaml_parse_file(args, initial_content=post)

        for required in ["author", "title"]:
            if (required not in meta or
                    not meta[required] or
                    meta[required] == "required"):
                print("'%s' required!" % required)
                # TODO, instead of terminating here, send the user back
                # to the EDITOR
                return

        pprint(crea.reply(
            meta["replyto"],
            message,
            title=meta["title"],
            author=meta["author"],
            meta=json_meta,
        ))

    elif args.command == "post" or args.command == "yaml":
        initmeta = {
            "title": args.title or "required",
            "author": args.author or "required",
            "category": args.category or "required",
            "tags": args.tags or [],
            "max_accepted_payout": "1000000.000 %s" % crea.symbol("CBD"),
            "percent_crea_dollars": 100,
            "allow_votes": True,
            "allow_curation_rewards": True,
        }

        post = frontmatter.Post("", **initmeta)
        meta, json_meta, body = yaml_parse_file(args, initial_content=post)

        # Default "app"
        if "app" not in json_meta:
            version = pkg_resources.require("creacli")[0].version
            json_meta["app"] = "CreaPy/{}".format(version)

        if not body:
            print("Empty body! Not posting!")
            return

        for required in ["author", "title", "category"]:
            if (required not in meta or
                    not meta[required] or
                    meta[required] == "required"):
                print("'%s' required!" % required)
                # TODO, instead of terminating here, send the user back
                # to the EDITOR
                return

        pprint(crea.post(
            meta["title"],
            body,
            author=meta["author"],
            category=meta["category"],
            meta=json_meta,
        ))

    elif args.command == "edit":
        original_post = crea.get_content(args.post)

        edited_message = None
        if original_post["id"] == "0.0.0":
            print("Can't find post %s" % args.post)
            return

        post = frontmatter.Post(original_post["body"], **{
            "title": original_post["title"] + " (immutable)",
            "author": original_post["author"] + " (immutable)",
            "tags": original_post["tags"]
        })

        meta, json_meta, edited_message = yaml_parse_file(args, initial_content=post)
        pprint(crea.edit(
            args.post,
            edited_message,
            replace=args.replace,
            meta=json_meta,
        ))

    elif args.command == "upvote" or args.command == "downvote":
        post = Post(args.post)
        if args.command == "downvote":
            weight = -float(args.weight)
        else:
            weight = +float(args.weight)
        if not args.voter:
            print("Not voter provided!")
            return
        pprint(post.vote(weight, voter=args.voter))

    elif args.command == "read":
        post_author, post_permlink = resolveIdentifier(args.post)

        if args.parents:
            # FIXME inconsistency, use @author/permlink instead!
            dump_recursive_parents(
                crea.rpc,
                post_author,
                post_permlink,
                args.parents,
                format=args.format
            )

        if not args.comments and not args.parents:
            post = crea.get_content(args.post)

            if post["id"] == "0.0.0":
                print("Can't find post %s" % args.post)
                return
            if args.format == "markdown":
                body = markdownify(post["body"])
            else:
                body = post["body"]

            if args.full:
                meta = {}
                for key in post:
                    if key in ["crea", "body"]:
                        continue
                    if isinstance(post[key], Amount):
                        meta[key] = str(post[key])
                    else:
                        meta[key] = post[key]
                yaml = frontmatter.Post(body, **meta)
                print(frontmatter.dumps(yaml))
            else:
                print(body)

        if args.comments:
            dump_recursive_comments(
                crea.rpc,
                post_author,
                post_permlink,
                format=args.format
            )

    elif args.command == "categories":
        categories = crea.get_categories(
            sort=args.sort,
            begin=args.category,
            limit=args.limit
        )
        t = PrettyTable(["name", "discussions", "payouts"])
        t.align = "l"
        for category in categories:
            t.add_row([
                category["name"],
                category["discussions"],
                category["total_payouts"],
            ])
        print(t)

    elif args.command == "list":
        list_posts(
            crea.get_posts(
                limit=args.limit,
                sort=args.sort,
                category=args.category,
                start=args.start
            ),
            args.columns
        )

    elif args.command == "replies":
        if not args.author:
            print("Please specify an author via --author\n "
                  "or define your default author with:\n"
                  "   CreaPy set default_author x")
        else:
            discussions = crea.get_replies(args.author)
            list_posts(discussions[0:args.limit])

    elif args.command == "transfer":
        pprint(crea.transfer(
            args.to,
            args.amount,
            args.asset,
            memo=args.memo,
            account=args.account
        ))

    elif args.command == "powerup":
        pprint(crea.transfer_to_vesting(
            args.amount,
            account=args.account,
            to=args.to
        ))

    elif args.command == "powerdown":
        pprint(crea.withdraw_vesting(
            args.amount,
            account=args.account,
        ))

    elif args.command == "convert":
        pprint(crea.convert(
            args.amount,
            account=args.account,
        ))

    elif args.command == "powerdownroute":
        pprint(crea.set_withdraw_vesting_route(
            args.to,
            percentage=args.percentage,
            account=args.account,
            auto_vest=args.auto_vest
        ))

    elif args.command == "balance":
        t = PrettyTable(["Account", "CREA", "CBD", "VESTS",
                         "VESTS (in CREA)", "Savings (CREA)",
                         "Savings (CBD)"])
        t.align = "r"
        if isinstance(args.account, str):
            args.account = [args.account]
        for a in args.account:
            b = crea.get_balances(a)
            t.add_row([
                a,
                b["balance"],
                b["cbd_balance"],
                b["vesting_shares"],
                b["vesting_shares_crea"],
                b["savings_balance"],
                b["savings_cbd_balance"]
            ])
        print(t)

    elif args.command == "history":
        header = ["#", "time (block)", "operation", "details"]
        if args.csv:
            import csv
            t = csv.writer(sys.stdout, delimiter=";")
            t.writerow(header)
        else:
            t = PrettyTable(header)
            t.align = "l"
        if isinstance(args.account, str):
            args.account = [args.account]
        if isinstance(args.types, str):
            args.types = [args.types]

        for a in args.account:
            for b in Account(a).rawhistory(
                first=args.first,
                limit=args.limit,
                only_ops=args.types,
                exclude_ops=args.exclude_types
            ):
                row = [
                    b[0],
                    "%s (%s)" % (b[1]["timestamp"], b[1]["block"]),
                    b[1]["op"][0],
                    format_operation_details(b[1]["op"], memos=args.memos),
                ]
                if args.csv:
                    t.writerow(row)
                else:
                    t.add_row(row)
        if not args.csv:
            print(t)

    elif args.command == "interest":
        t = PrettyTable(["Account",
                         "Last Interest Payment",
                         "Next Payment",
                         "Interest rate",
                         "Interest"])
        t.align = "r"
        if isinstance(args.account, str):
            args.account = [args.account]
        for a in args.account:
            i = crea.interest(a)

            t.add_row([
                a,
                i["last_payment"],
                "in %s" % strfage(i["next_payment_duration"]),
                "%.1f%%" % i["interest_rate"],
                "%.3f %s" % (i["interest"], crea.symbol("CBD")),
            ])
        print(t)

    elif args.command == "permissions":
        account = Account(args.account)
        print_permissions(account)

    elif args.command == "allow":
        if not args.foreign_account:
            from creapybase.account import PasswordKey
            pwd = get_terminal(text="Password for Key Derivation: ", confirm=True)
            args.foreign_account = format(PasswordKey(args.account, pwd, args.permission).get_public(), "DWB")
        pprint(crea.allow(
            args.foreign_account,
            weight=args.weight,
            account=args.account,
            permission=args.permission,
            threshold=args.threshold
        ))

    elif args.command == "disallow":
        pprint(crea.disallow(
            args.foreign_account,
            account=args.account,
            permission=args.permission,
            threshold=args.threshold
        ))

    elif args.command == "updatememokey":
        if not args.key:
            # Loop until both match
            from creapybase.account import PasswordKey
            pw = get_terminal(text="Password for Memo Key: ", confirm=True, allowedempty=False)
            memo_key = PasswordKey(args.account, pw, "memo")
            args.key = format(memo_key.get_public_key(), "DWB")
            memo_privkey = memo_key.get_private_key()
            # Add the key to the wallet
            if not args.nobroadcast:
                crea.wallet.addPrivateKey(memo_privkey)
        pprint(crea.update_memo_key(
            args.key,
            account=args.account
        ))

    elif args.command == "newaccount":
        import getpass
        while True:
            pw = getpass.getpass("New Account Passphrase: ")
            if not pw:
                print("You cannot chosen an empty password!")
                continue
            else:
                pwck = getpass.getpass(
                    "Confirm New Account Passphrase: "
                )
                if (pw == pwck):
                    break
                else:
                    print("Given Passphrases do not match!")
        pprint(crea.create_account(
            args.accountname,
            creator=args.account,
            password=pw,
        ))

    elif args.command == "importaccount":
        from creapybase.account import PasswordKey
        import getpass
        password = getpass.getpass("Account Passphrase: ")
        account = Account(args.account)
        imported = False

        if "owner" in args.roles:
            owner_key = PasswordKey(args.account, password, role="owner")
            owner_pubkey = format(owner_key.get_public_key(), "DWB")
            if owner_pubkey in [x[0] for x in account["owner"]["key_auths"]]:
                print("Importing owner key!")
                owner_privkey = owner_key.get_private_key()
                crea.wallet.addPrivateKey(owner_privkey)
                imported = True

        if "active" in args.roles:
            active_key = PasswordKey(args.account, password, role="active")
            active_pubkey = format(active_key.get_public_key(), "DWB")
            if active_pubkey in [x[0] for x in account["active"]["key_auths"]]:
                print("Importing active key!")
                active_privkey = active_key.get_private_key()
                crea.wallet.addPrivateKey(active_privkey)
                imported = True

        if "posting" in args.roles:
            posting_key = PasswordKey(args.account, password, role="posting")
            posting_pubkey = format(posting_key.get_public_key(), "DWB")
            if posting_pubkey in [x[0] for x in account["posting"]["key_auths"]]:
                print("Importing posting key!")
                posting_privkey = posting_key.get_private_key()
                crea.wallet.addPrivateKey(posting_privkey)
                imported = True

        if "memo" in args.roles:
            memo_key = PasswordKey(args.account, password, role="memo")
            memo_pubkey = format(memo_key.get_public_key(), "DWB")
            if memo_pubkey == account["memo_key"]:
                print("Importing memo key!")
                memo_privkey = memo_key.get_private_key()
                crea.wallet.addPrivateKey(memo_privkey)
                imported = True

        if not imported:
            print("No matching key(s) found. Password correct?")

    elif args.command == "sign":
        if args.file and args.file != "-":
            if not os.path.isfile(args.file):
                raise Exception("File %s does not exist!" % args.file)
            with open(args.file) as fp:
                tx = fp.read()
        else:
            tx = sys.stdin.read()
        tx = eval(tx)
        pprint(crea.sign(tx))

    elif args.command == "broadcast":
        if args.file and args.file != "-":
            if not os.path.isfile(args.file):
                raise Exception("File %s does not exist!" % args.file)
            with open(args.file) as fp:
                tx = fp.read()
        else:
            tx = sys.stdin.read()
        tx = eval(tx)
        crea.broadcast(tx)

    elif args.command == "orderbook":
        if args.chart:
            try:
                import numpy
                import Gnuplot
                from itertools import accumulate
            except:
                print("To use --chart, you need gnuplot and gnuplot-py installed")
                sys.exit(1)
        dex = Dex(crea)
        orderbook = dex.returnOrderBook()

        if args.chart:
            g = Gnuplot.Gnuplot()
            g.title("Crea internal market - CBD:CREA")
            g.xlabel("price in CBD")
            g.ylabel("volume")
            g("""
                set style data line
                set term xterm
                set border 15
            """)
            xbids = [x["price"] for x in orderbook["bids"]]
            ybids = list(accumulate([x["cbd"] for x in orderbook["bids"]]))
            dbids = Gnuplot.Data(xbids, ybids, with_="lines")
            xasks = [x["price"] for x in orderbook["asks"]]
            yasks = list(accumulate([x["cbd"] for x in orderbook["asks"]]))
            dasks = Gnuplot.Data(xasks, yasks, with_="lines")
            g("set terminal dumb")
            g.plot(dbids, dasks)  # write SVG data directly to stdout ...

        t = {}
        # Bid side
        bidscrea = 0
        bidscbd = 0
        t["bids"] = PrettyTable([
            "CBD", "sum CBD", "CREA", "sum CREA", "price"
        ])
        for i, o in enumerate(orderbook["asks"]):
            bidscbd += orderbook["bids"][i]["cbd"]
            bidscrea += orderbook["bids"][i]["crea"]
            t["bids"].add_row([
                "%.3f Ṩ" % orderbook["bids"][i]["cbd"],
                "%.3f ∑" % bidscbd,
                "%.3f ȿ" % orderbook["bids"][i]["crea"],
                "%.3f ∑" % bidscrea,
                "%.3f Ṩ/ȿ" % orderbook["bids"][i]["price"],
            ])

        # Ask side
        askscrea = 0
        askscbd = 0
        t["asks"] = PrettyTable([
            "price", "CREA", "sum CREA", "CBD", "sum CBD"
        ])
        for i, o in enumerate(orderbook["asks"]):
            askscbd += orderbook["asks"][i]["cbd"]
            askscrea += orderbook["asks"][i]["crea"]
            t["asks"].add_row([
                "%.3f Ṩ/ȿ" % orderbook["asks"][i]["price"],
                "%.3f ȿ" % orderbook["asks"][i]["crea"],
                "%.3f ∑" % askscrea,
                "%.3f Ṩ" % orderbook["asks"][i]["cbd"],
                "%.3f ∑" % askscbd
            ])

        book = PrettyTable(["bids", "asks"])
        book.add_row([t["bids"], t["asks"]])
        print(book)

    elif args.command == "buy":
        if args.asset == crea.symbol("CBD"):
            price = 1.0 / args.price
        else:
            price = args.price
        dex = Dex(crea)
        pprint(dex.buy(
            args.amount,
            args.asset,
            price,
            account=args.account
        ))

    elif args.command == "sell":
        if args.asset == crea.symbol("CBD"):
            price = 1.0 / args.price
        else:
            price = args.price
        dex = Dex(crea)
        pprint(dex.sell(
            args.amount,
            args.asset,
            price,
            account=args.account
        ))

    elif args.command == "cancel":
        dex = Dex(crea)
        pprint(
            dex.cancel(args.orderid)
        )

    elif args.command == "approvewitness":
        pprint(crea.approve_witness(
            args.witness,
            account=args.account
        ))

    elif args.command == "disapprovewitness":
        pprint(crea.disapprove_witness(
            args.witness,
            account=args.account
        ))

    elif args.command == "repost":
        pprint(crea.repost(
            args.identifier,
            account=args.account
        ))

    elif args.command == "follow":
        pprint(crea.follow(
            args.follow,
            what=args.what,
            account=args.account
        ))

    elif args.command == "unfollow":
        pprint(crea.unfollow(
            args.unfollow,
            what=args.what,
            account=args.account
        ))

    elif args.command == "setprofile":
        from creapy.profile import Profile
        keys = []
        values = []
        if args.pair:
            for pair in args.pair:
                key, value = pair.split("=")
                keys.append(key)
                values.append(value)
        if args.variable and args.value:
            keys.append(args.variable)
            values.append(args.value)

        profile = Profile(keys, values)

        account = Account(args.account)
        account["json_metadata"] = Profile(
            account["json_metadata"]
            if account["json_metadata"]
            else {}
        )
        account["json_metadata"].update(profile)

        pprint(crea.update_account_profile(
            account["json_metadata"],
            account=args.account
        ))

    elif args.command == "delprofile":
        from .profile import Profile
        account = Account(args.account)
        account["json_metadata"] = Profile(account["json_metadata"])

        for var in args.variable:
            account["json_metadata"].remove(var)

        pprint(crea.update_account_profile(
            account["json_metadata"],
            account=args.account
        ))

    elif args.command == "witnessupdate":

        witness = Witness(args.witness)
        props = witness["props"]
        if args.account_creation_fee:
            props["account_creation_fee"] = str(Amount("%f CREA" % args.account_creation_fee))
        if args.maximum_block_size:
            props["maximum_block_size"] = args.maximum_block_size
        if args.cbd_interest_rate:
            props["cbd_interest_rate"] = int(args.cbd_interest_rate * 100)

        pprint(crea.witness_update(
            args.signing_key or witness["signing_key"],
            args.url or witness["url"],
            props,
            account=args.witness
        ))

    elif args.command == "witnesscreate":
        props = {
            "account_creation_fee": str(Amount("%f CREA" % args.account_creation_fee)),
            "maximum_block_size": args.maximum_block_size,
            "cbd_interest_rate": int(args.cbd_interest_rate * 100)
        }
        pprint(crea.witness_update(
            args.signing_key,
            args.url,
            props,
            account=args.witness
        ))

    else:
        print("No valid command given")


args = None

if __name__ == '__main__':
    main()
