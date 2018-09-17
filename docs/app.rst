*****************
CreaPy Executable
*****************

Swiss army knife for interacting with the Crea blockchain.

Quickstart
##########

You can start using 'creapy' by going through out Crea hosted quick start
guide. Just run::

    creapy read @jared/creacli-quickstart

Available Commands
##################

Adding keys (for posting)
~~~~~~~~~~~~~~~~~~~~~~~~~

CreaPy comes with its own encrypted wallet to which keys need to be
added:::

    creapy addkey

On first run, you will be asked to provide a new passphrase that you
will need to provide every time you want to post on the Crea network.
If you chose an *empty* password, your keys will be stored in plain text
which allows automated posting but exposes your private key to your
local user.

List available Keys and accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can list the installed keys using:::

    creapy listkeys

This command will give the list of public keys to which the private keys
are available.::

    creapy listaccounts

This command tries to resolve the public keys into account names
registered on the network (experimental).

Configuration
~~~~~~~~~~~~~

``creapy`` comes with its own configuration:::

    creapy set default_voter <account-name>
    creapy set default_author <account-name>

All configuration variables are provided with ``creapy set --help``
You can see your local configuration by calling::

    creapy config

Listing
~~~~~~~

``creapy`` can list, sort, and filter for posts on the Crea blockchain.
You can read about the parameters by::

    creapy list --help

Example:::

    $ creapy list --limit 3 --sort payout
    +----------------------------------------+------------------------------------------------+----------+---------+------------------+---------------+
    | identifier                             | title                                          | category | replies |            votes |       payouts |
    +----------------------------------------+------------------------------------------------+----------+---------+------------------+---------------+
    | @donaldtrump/lets-talk-politics        | Let's Talk Politics and the U.S. 2016 Election | politics |    20   | 1020791260074419 | 14106.752 CBD |
    | @nextgencrypto/bex-price-speculation   | CREA Price Speculation                          | crea     |    14   |  777027533714240 | 11675.872 CBD |
    | @clayop/lets-request-bex-to-poloniex   | Let's Request CREA to Poloniex                  | crea     |    8    |  988929602909199 | 10530.426 CBD |
    +----------------------------------------+------------------------------------------------+----------+---------+------------------+---------------+

Reading
~~~~~~~

The subcommand ``read`` allows to read posts and replies from Crea by
providing the post *identifier*. The identifier takes the form::

    @author/permlink

The subcommands takes the optional parameters:

-  ``--full``: show the posts meta data as YAML formatted frontmatter
-  ``--comments``: to show all comments and replies made to that post
-  ``--parents x``: Show ``x`` parent posts

See examples:::

    $ creapy read "@jared/creapy-readme"

    [this readme]

    $ creapy read "@jared/crea-python" --comments

     ---
     author: puppies
     permlink: re-crea-python
     reply: '@puppies/re-crea-python'
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
     permlink: re-jared-crea-python-20160414t145522693z
     reply: '@dantheman/re-jared-crea-python-20160414t145522693z'
     ---

     This is great work jared!  Thanks for supporting !

Categories
~~~~~~~~~~

Existing categories can be listed via:::

    creapy categories --limit 10

Please see the corresponding help page for further options:::

    creapy categories --help

Posting
~~~~~~~

To post new content, you need to provide

-  the author,
-  a permlink, and
-  a title

For posting the "posting-key" of the author needs to be added to the
wallet.

Additionally, a ``--category`` can be added as well.::

    echo "Texts" | creapy post --author "<author>" --category "<category>" --title "<posttitle>" --permlink "<permlink>"
    cat filename | creapy post --author "<author>" --category "<category>" --title "<posttitle>" --permlink "<permlink>"

If you want to provide mulitple tags to your post, you can add it to the
frontmatter like this:::

   ---
   author: ......
   category: .......
   title: .......
   tags:
     - introduceyourself
     - crea
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

    echo "Texts" | creapy reply --file - "@jared/crea-python" --author "<author>"
    cat filename | creapy reply --file - "@jared/crea-python" --author "<author>"

If you want to use your favorit ``EDITOR``, you can do this by:::

    creapy reply "@jared/crea-python"

Editing
~~~~~~~

With creapy, you can edit your own posts with your favorite text editor
(as defined in the environmental variable ``EDITOR``):::

    $ creapy "@jared/edit-test"
    $ EDITOR="nano" creapy "@jared/edit-test"

If you want to replace your entire post and not *patch* it, you can add
the ``--replace`` flag.

Voting
~~~~~~

With ``creapy``, you can up-/downvote any post with your installed
accounts:::

    creapy upvote --voter <voter> <identifier>
    creapy downvote --voter <voter> <identifier>

providing the post *identifier*. The identifier takes the form::

    @author/permlink

You can further define the weight (default 100%) manually with
``--weight``.

Replies
~~~~~~~

``creapy`` can show replies to posts made by any author:::

    creapy replies --author jared

If ``--author`` is not provided, the *default* author as defined with
``creapy set author`` will be taken. Further options are: ``--limit``.

Transfer CREA
~~~~~~~~~~~~~~

CREA can be transfered via::

    creapy transfer receipient 100.000 CREA

If ``--author`` is not provided, the *default* account as defined with
``creapy set author`` will be taken.

Buy/Sell CREA/CBD
~~~~~~~~~~~~~~~~~~

You can of course sell your assets in the internal decentralized exchange that
is integrated into the CREA blockchain by using:::

    creapy buy <amount> CREA <price in CBD per CREA>
    creapy buy <amount> CBD <price in CBD per CREA>

    creapy sell <amount> CREA <price in CBD per CREA>
    creapy sell <amount> CBD <price in CBD per CREA>

Powerup/Powerdown
~~~~~~~~~~~~~~~~~

You can powerup/down your account with creapy using:::

    creapy powerup 100   # in CREA
    creapy powerdown 10000   # in VESTS

If ``--author``/``--to`` are not provided, the *default* account as defined with
``creapy set author`` will be taken.

To route your powerdows to another account automatically, you can use
``powerdownroute``. Read more in the corresponding help::

   creapy powerdownroute -h

Convert
~~~~~~~

This method allows to convert CREADollar to CREA using the internal conversion
rate after 1 week. Note, that when you convert, you will obtain the
corresponding amount of CREA only after waiting 1 week. ::

    creapy convert --account <account>


Balances
~~~~~~~~

Get an account's balance with::

    creapy balance <account>

If ``<account>`` is not provided, the *default* account will be taken.

Interest
~~~~~~~~

CREADollar pay interest. You can see the details for any account using:::

    creapy interest <account>

History
~~~~~~~

You can get an accounts history by using::

    creapy history <account>

Furthermore you can filter by ``types`` and limit the result by
transaction number. More information can be found by calling ``creapy
history -h``.


Permissions
~~~~~~~~~~~

Any account permission can be inspected using::

    creapy permissions [<account>]

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

    creapy allow --account <account> --weight 1 --permission posting --threshold 1 <foreign_account>
    creapy disallow --permission <permissions> <foreign_account>

More details and the default parameters can be found via:::

    creapy allow --help
    creapy disallow --help

Update Memo Key
~~~~~~~~~~~~~~~

The memo key of your account can be updated with

    creapy updatememokey --key <KEY>

If no ``key`` is provided, it will ask for a password from which the
key will be derived

Create a new account
~~~~~~~~~~~~~~~~~~~~

CreaPy let's you create new accounts on the Crea blockchain.

.. note::

    Creating new accounts will cost you a fee!

It works like this:

    creapy newaccount <accountname>

and it will ask you to provide a new password. During creation, creapy
will derive the new keys from the password (and the account name) and
store them in the wallet (except for the owner key)

.. note::

    ``newaccount`` will **not** store the owner private key in the
    wallet!

Import Account
~~~~~~~~~~~~~~

You can import your existing account into creapy by using

    creapy importaccount --account <accountname>

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
With creapy, you can also approve and disapprove witnesses who are
producing blocks on the Crea blockchain:::

    creapy approvewitness <witnessname>
    creapy disapprovewitness <witnessname>

Info
~~~~
CreaPy can read data from the blockchain and present it to the user in
tabular form. It can automatically identify:

* block numbers (``340``)
* account names (``creapy``)
* public keys (``DWBxxxxxxxxxx``)
* post identifiers (``@<accountname>/<permlink>``)
* general blockchain parameters

The corresponding data can be presented using:::

    creapy info [block_num [account name [pubkey [identifier]]]]

Repost
~~~~~~~
Existing posts can be reposted using:::

    creapy repost [--account <account>] @author/permlink

Follow/Unfollow
~~~~~~~~~~~~~~~
You can follow and unfollow someones blog posts by:::

    creapy follow <accountname>
    creapy unfollow <accountname>

Profile
~~~~~~~
CreaPy can help you set your profile variables (through
``json_metadata``):::

    creapy setprofile profile.url "http://chainsquad.com"
    creapy setprofile --pair "profile.url=http://chainsquad.com" "profile.name=ChainSquad GmbH"

Keys can be removed with:::

    creapy delprofile profile.url
