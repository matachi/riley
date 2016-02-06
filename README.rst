=====
Riley
=====

| Author: Daniel Jonsson
| License: `MIT License <COPYING>`_

Setup
=====

For development::

    $ make install-dev

Normal usage::

    $ make install

Usage
=====

Example commands (still work-in-progess)::

    $ source env/bin/activate
    $ riley insert linux-action-show http://feeds2.feedburner.com/TheLinuxActionShowOGG
    $ riley fetch
    $ riley list
    ... episode list ...
    $ riley download
    ... downloads the last episode ...

List latest episodes::

    $ riley list | head

Browse episodes::

    $ riley list | less

List downloaded episodes::

    $ ls ~/Music/Riley

List downloaded episodes ordered by publish date::

    $ ls -ltr ~/Music/Riley

Listen to the oldest episode among your downloaded episodes::

    $ mpv "`ls -tr $PWD/Music/Riley/* | head -n 1`"

Listen to the oldest episode among your downloaded episodes and delete it
afterwards::

    $ FILE=$(ls -tr $PWD/Music/Riley/* | head -n 1); mpv $FILE && rm -i $FILE

Clean config
============

Delete config files::

    $ make clean

Run tests
=========

::

    $ make test
