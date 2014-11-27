.. -*- coding: utf-8; mode: rst -*-


==========
aggregator
==========

The ``aggregator`` is an advanced storage and retrival server, optimized to
store and query RSS feeds.

This package is the core of the application.


Developer Instructions
======================


Requirements
------------

This guide assumes that you develop the ``aggregator`` on a ``Debian/GNU Linux``
version ``Wheezy``.

.. code:: sh

    sudo apt-get install python-virtualenv \
    libsqlite3-0 \
    mongodb-server


Virtualenv
----------

There are several tools that help to manage python virtualenvs.  If you are
already familiar with ``virtualenvwrapper`` you can use it.  If not just follow
the following suggestions:

.. code:: sh

    cd
    mkdir ve
    cd ve
    vitutualenv aggregator-ve
    . aggregator-ve/bin/activate

.. warning::

    Remember to activate the virtualenv every time you start developing.


Source code
-----------

The source code is manage with ``git`` using the ``git-flow`` work-flow.

You should have an account with writing privileges.

.. code:: sh

    cd
    mkdir dev
    cd dev
    git clone git@git.ahref.eu:aggregator/aggregator.git
    cd aggregator
    git checkout -b develop origin/develop


When a new release is ready the developer must increase at least the patch level
(we do not have a automatic builder/continuous integration system that use the
build number):

- Bump the version number in the file ``version.txt``
- Tag with a lightweight tag the bump version commit
- Merge the ``develop`` branch in ``master``
- Push the ``master`` branch, including the tags

For example to bump the version to ``0.0.1.0``, assuming that we start in the
``develop`` branch:

.. code:: sh

    NEW_VERSION="0.0.1.0"
    printf "%s" "${NEW_VERSION}" > version.txt
    git add version.txt
    git commit -m "Bump version to ${NEW_VERSION}"
    git tag v"${NEW_VERSION}"
    git checkout master
    git merge develop --ff-only
    git push
    git push --tags


Starting with git 1.8.3 the last two command can be replaced with:

.. code:: sh

    git push --follow-tags

You can check that the braches are aligned with:

.. code:: sh

    DEVEL_HASH=`git log --format=%h -n1 origin/develop`
    MASTER_HASH=`git log --format=%h -n1 origin/master`
    test "X${DEVEL_HASH}" = "X${MASTER_HASH}" || \
    printf "WARNING: something went wrong\n" && \
    printf "NOTICE: heads of the branches OK\n"


Later you can start to develop again in develop:

.. code:: sh

    git checkout develop


Development
-----------

The ``aggregator`` is developed as a python packages.  The ``develop`` command
will download and install the requirements.

.. code:: sh

    python setup.py develop

You can start developing following the issues for your milestone.


Testing
-------

``aggregator`` follow a strict testing procedure.  Before every commit you must
check that the test pass and that the source code respect the best practices
defined by the ``python`` community.

.. code:: sh

    python setup.py test
    python setup.py flake8

An improved test runner is:

.. code:: sh

    nosetests -c nose.cfg

This will open a ``ipdb`` shell in case of errors and failures and provide a
coverage report.


Documentation
-------------

The developer documentation is made with ``sphinx`` and in particular with
``sphinxcontrib.autohttp.flask``.  A quick start:

.. code:: sh

    cd docs
    make singlehtml
    xdg-open build/singlehtml/index.html


Manage command
--------------

For convenience other flask related commands are available, just run
``aggregator`` to see the list.


Utility command
---------------

1. ``update_url``: command line utility for updating baseurl of image stored in
   enclourse of entry.

    Options:

    .. code:: sh

        aggregator update_url -o [all] | [object_id] -p old_url -t new_url -m dryrun

    Example:

    .. code:: sh

        aggregator update_url -o all \
        -p http://storygrant.civiclinks.it/ \
        -t https://storygrant.civiclinks.it/ \
        -m dryrun


API KEY collection creation
---------------------------

To create apikey collection, check that the Db is "aggregator" and change
username and password. Run below command from shell:

.. code:: sh

  mongoimport -d aggregator_test -c apikey  --jsonArray aggregator/assets/data/apikey.json

Or if you have authentication in mongo:

.. code:: sh

  mongoimport -d aggregator_test -c apikey --username user --password pass \
  --jsonArray --file aggregator/assets/data/apikey.json


For adding a new key: run below command with after replacing "apikey" with a
  random string and replace "applicationname" with proper application name

..code:: sh

    aggregator add_api_key -k "apikey" -a "applicationname"
