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

Clean config
============

Delete config files::

    $ make clean

Run tests
=========

::

    $ make test
