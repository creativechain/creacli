*****************
dPayPy Executable
*****************

Swiss army knife for interacting with the dPay blockchain.

Quickstart
##########

You can start using 'dpaypy' by going through out dPay hosted quick start
guide. Just run::

    dpaypy read @jared/dpaycli-quickstart

Available Commands
##################

Adding keys (for posting)
~~~~~~~~~~~~~~~~~~~~~~~~~

dPayPy comes with its own encrypted wallet to which keys need to be
added:::

    dpaypy addkey

On first run, you will be asked to provide a new passphrase that you
will need to provide every time you want to post on the dPay network.
If you chose an *empty* password, your keys will be stored in plain text
which allows automated posting but exposes your private key to your
local user.

List available Keys and accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can list the installed keys using:::

    dpaypy listkeys

This command will give the list of public keys to which the private keys
are available.::

    dpaypy listaccounts

This command tries to resolve the public keys into account names
registered on the network (experimental).

Configuration
~~~~~~~~~~~~~

``dpaypy`` comes with its own configuration:::

    dpaypy set default_voter <account-name>
    dpaypy set default_author <account-name>

All configuration variables are provided with ``dpaypy set --help``
You can see your local configuration by calling::

    dpaypy config

Listing
~~~~~~~

``dpaypy`` can list, sort, and filter for posts on the dPay blockchain.
You can read about the parameters by::

    dpaypy list --help

Example:::

    $ dpaypy list --limit 3 --sort payout
    +----------------------------------------+------------------------------------------------+----------+---------+------------------+---------------+
    | identifier                             | title                                          | category | replies |            votes |       payouts |
    +----------------------------------------+------------------------------------------------+----------+---------+------------------+---------------+
    | @donaldtrump/lets-talk-politics        | Let's Talk Politics and the U.S. 2016 Election | politics |    20   | 1020791260074419 | 14106.752 BBD |
    | @nextgencrypto/bex-price-speculation   | BEX Price Speculation                          | dpay     |    14   |  777027533714240 | 11675.872 BBD |
    | @clayop/lets-request-bex-to-poloniex   | Let's Request BEX to Poloniex                  | dpay     |    8    |  988929602909199 | 10530.426 BBD |
    +----------------------------------------+------------------------------------------------+----------+---------+------------------+---------------+

Reading
~~~~~~~

The subcommand ``read`` allows to read posts and replies from dPay by
providing the post *identifier*. The identifier takes the form::

    @author/permlink

The subcommands takes the optional parameters:

-  ``--full``: show the posts meta data as YAML formatted frontmatter
-  ``--comments``: to show all comments and replies made to that post
-  ``--parents x``: Show ``x`` parent posts

See examples:::

    $ dpaypy read "@jared/dpaypy-readme"

    [this readme]

    $ dpaypy read "@jared/dpay-python" --comments

     ---
     author: puppies
     permlink: re-dpay-python
     reply: '@puppies/re-dpay-python'
     ---

     Great work Jared.  Your libraries make working with graphene chains truly a joy.
       ---
       author: jared
       permlink: test-post
       reply: '@jared/test-post'
       ---

       Thank you, I enjoy writing python a lot myself!
     ---
     author: nomoreheroes
     permlink: re-jared-dpay-python-20160414t145522693z
     reply: '@dantheman/re-jared-dpay-python-20160414t145522693z'
     ---

     This is great work jared!  Thanks for supporting !

Categories
~~~~~~~~~~

Existing categories can be listed via:::

    dpaypy categories --limit 10

Please see the corresponding help page for further options:::

    dpaypy categories --help

Posting
~~~~~~~

To post new content, you need to provide

-  the author,
-  a permlink, and
-  a title

For posting the "posting-key" of the author needs to be added to the
wallet.

Additionally, a ``--category`` can be added as well.::

    echo "Texts" | dpaypy post --author "<author>" --category "<category>" --title "<posttitle>" --permlink "<permlink>"
    cat filename | dpaypy post --author "<author>" --category "<category>" --title "<posttitle>" --permlink "<permlink>"

If you want to provide mulitple tags to your post, you can add it to the
frontmatter like this:::

   ---
   author: ......
   category: .......
   title: .......
   tags:
     - introduceyourself
     - dpay
     - art
   ---

Replying
~~~~~~~~

Here, the same parameters as for simply posting new content are
available except that instead of ``--category`` a ``replyto`` has to be
provided to identify the post that you want the reply to be posted to.
The ``replyto`` parameter takes the following form:::

    @author/permlink

E.g:::

    echo "Texts" | dpaypy reply --file - "@jared/dpay-python" --author "<author>"
    cat filename | dpaypy reply --file - "@jared/dpay-python" --author "<author>"

If you want to use your favorit ``EDITOR``, you can do this by:::

    dpaypy reply "@jared/dpay-python"

Editing
~~~~~~~

With dpaypy, you can edit your own posts with your favorite text editor
(as defined in the environmental variable ``EDITOR``):::

    $ dpaypy "@jared/edit-test"
    $ EDITOR="nano" dpaypy "@jared/edit-test"

If you want to replace your entire post and not *patch* it, you can add
the ``--replace`` flag.

Voting
~~~~~~

With ``dpaypy``, you can up-/downvote any post with your installed
accounts:::

    dpaypy upvote --voter <voter> <identifier>
    dpaypy downvote --voter <voter> <identifier>

providing the post *identifier*. The identifier takes the form::

    @author/permlink

You can further define the weight (default 100%) manually with
``--weight``.

Replies
~~~~~~~

``dpaypy`` can show replies to posts made by any author:::

    dpaypy replies --author jared

If ``--author`` is not provided, the *default* author as defined with
``dpaypy set author`` will be taken. Further options are: ``--limit``.

Transfer BEX
~~~~~~~~~~~~~~

BEX can be transfered via::

    dpaypy transfer receipient 100.000 BEX

If ``--author`` is not provided, the *default* account as defined with
``dpaypy set author`` will be taken.

Buy/Sell BEX/BBD
~~~~~~~~~~~~~~~~~~

You can of course sell your assets in the internal decentralized exchange that
is integrated into the BEX blockchain by using:::

    dpaypy buy <amount> BEX <price in BBD per BEX>
    dpaypy buy <amount> BBD <price in BBD per BEX>

    dpaypy sell <amount> BEX <price in BBD per BEX>
    dpaypy sell <amount> BBD <price in BBD per BEX>

Powerup/Powerdown
~~~~~~~~~~~~~~~~~

You can powerup/down your account with dpaypy using:::

    dpaypy powerup 100   # in BEX
    dpaypy powerdown 10000   # in VESTS

If ``--author``/``--to`` are not provided, the *default* account as defined with
``dpaypy set author`` will be taken.

To route your powerdows to another account automatically, you can use
``powerdownroute``. Read more in the corresponding help::

   dpaypy powerdownroute -h

Convert
~~~~~~~

This method allows to convert BEXDollar to BEX using the internal conversion
rate after 1 week. Note, that when you convert, you will obtain the
corresponding amount of BEX only after waiting 1 week. ::

    dpaypy convert --account <account>


Balances
~~~~~~~~

Get an account's balance with::

    dpaypy balance <account>

If ``<account>`` is not provided, the *default* account will be taken.

Interest
~~~~~~~~

BEXDollar pay interest. You can see the details for any account using:::

    dpaypy interest <account>

History
~~~~~~~

You can get an accounts history by using::

    dpaypy history <account>

Furthermore you can filter by ``types`` and limit the result by
transaction number. More information can be found by calling ``dpaypy
history -h``.


Permissions
~~~~~~~~~~~

Any account permission can be inspected using::

    dpaypy permissions [<account>]

The take the following form::

    +------------+-----------+-----------------------------------------------------------+
    | Permission | Threshold |                                               Key/Account |
    +------------+-----------+-----------------------------------------------------------+
    |      owner |         2 |                                                 jared (1) |
    |            |           | DWB7mgtsF5XPU9tokFpEz2zN9sQ89oAcRfcaSkZLsiqfWMtRDNKkc (1) |
    +------------+-----------+-----------------------------------------------------------+
    |     active |         1 | DWB6quoHiVnmiDEXyz4fAsrNd28G6q7qBCitWbZGo4pTfQn8SwkzD (1) |
    +------------+-----------+-----------------------------------------------------------+
    |    posting |         1 |                                          nomoreheroes (1) |
    |            |           | DWB6xpuUdyoRkRJ1GQmrHeNiVC3KGadjrBayo25HaTyBxBCQNwG3j (1) |
    |            |           | DWB8aJtoKdTsrRrWg3PB9XsbsCgZbVeDhQS3VUM1jkcXfVSjbv4T8 (1) |
    +------------+-----------+-----------------------------------------------------------+

The permissions are either **owner** (full control over the account),
**active** (full control, except for changing the owner), and
**posting** (for posting and voting). The keys can either be a public
key or another account name while the number behind shows the weight of
the entry. If the weight is smaller than the threshold, a single
signature will not suffice to validate a transaction

Allow/Disallow
~~~~~~~~~~~~~~

Permissions can be changed using:::

    dpaypy allow --account <account> --weight 1 --permission posting --threshold 1 <foreign_account>
    dpaypy disallow --permission <permissions> <foreign_account>

More details and the default parameters can be found via:::

    dpaypy allow --help
    dpaypy disallow --help

Update Memo Key
~~~~~~~~~~~~~~~

The memo key of your account can be updated with

    dpaypy updatememokey --key <KEY>

If no ``key`` is provided, it will ask for a password from which the
key will be derived

Create a new account
~~~~~~~~~~~~~~~~~~~~

dPayPy let's you create new accounts on the dPay blockchain.

.. note::

    Creating new accounts will cost you a fee!

It works like this:

    dpaypy newaccount <accountname>

and it will ask you to provide a new password. During creation, dpaypy
will derive the new keys from the password (and the account name) and
store them in the wallet (except for the owner key)

.. note::

    ``newaccount`` will **not** store the owner private key in the
    wallet!

Import Account
~~~~~~~~~~~~~~

You can import your existing account into dpaypy by using

    dpaypy importaccount --account <accountname>

It will ask you to provide the passphrase from which the private key
will be derived. If you already have a private key, you can use `addkey`
instead.

Sign/Broadcast Transaction
~~~~~~~~~~~~~~~~~~~~~~~~~~

Unsigned (but properly prepared) transactions can be signed with
``sign``. Signed transactions can be broadcast using ``broadcast``.
These feature is described in :doc:`<coldstorage.rst>` and :doc:`<multisig.rst>`.

Approve/Disapprove Witnesses
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
With dpaypy, you can also approve and disapprove witnesses who are
producing blocks on the dPay blockchain:::

    dpaypy approvewitness <witnessname>
    dpaypy disapprovewitness <witnessname>

Info
~~~~
dPayPy can read data from the blockchain and present it to the user in
tabular form. It can automatically identify:

* block numbers (``340``)
* account names (``dpaypy``)
* public keys (``DWBxxxxxxxxxx``)
* post identifiers (``@<accountname>/<permlink>``)
* general blockchain parameters

The corresponding data can be presented using:::

    dpaypy info [block_num [account name [pubkey [identifier]]]]

Repost
~~~~~~~
Existing posts can be reposted using:::

    dpaypy repost [--account <account>] @author/permlink

Follow/Unfollow
~~~~~~~~~~~~~~~
You can follow and unfollow someones blog posts by:::

    dpaypy follow <accountname>
    dpaypy unfollow <accountname>

Profile
~~~~~~~
dPayPy can help you set your profile variables (through
``json_metadata``):::

    dpaypy setprofile profile.url "http://chainsquad.com"
    dpaypy setprofile --pair "profile.url=http://chainsquad.com" "profile.name=ChainSquad GmbH"

Keys can be removed with:::

    dpaypy delprofile profile.url
