Reliable Discord-client IRC Daemon (rdircd)
===========================================

Python3/asyncio daemon to present personal discord client as local irc server,
with a list of channels corresponding to ones available on all joined "discord
servers" (group of users/channels with its own theme/auth/rules on discord).

One additional "reliable" quirk is that the plan is to have it actually connect
to discord under two separate accounts ("main" and "ghost"), and have these
monitor same channels to detect when stuff posted by the "main" acc doesn't make it,
or any other messages don't get relayed to either of the two,
which is unfortunately an issue that either discord api or other clients that
I've used seem to have from time to time.

Under development and not ready for use yet.


Usage
-----

- Go to https://discordapp.com/developers/applications/#top and register your
  fork or instance of the app.

  Discord client_id can be hardcoded into the app, so that every user don't need
  to go get it, but as I'm probably the only one using this one, don't see much
  reason to bother.

- In General Information tab there, find "Client ID" (long number) and "Client
  Secret" (alphanumeric) and copy these into "[discord]" section of
  ~/.rdircd.ini file like this one::

    [irc]
    password = xyzxyz123

    [discord]
    client-id = 157730590492196864
    client-secret = s1H7hzOI9EwzFHhTT4TChoQjYKf6g350hbMN33OJJoU

  That ini file will be updated with [auth] section by the script to store
  OAuth2 credentials, but it should not touch anything else there.

  If whole file or that client-id is missing there,
  script will prompt for it interactively.

- Run ./rdircd and it will present an URL for browser and a prompt for
  redirected-to URL after access is granted there - fill that in.

- Connect IRC client to localhost:6667 with the password from ini above.

  Password can be omitted or empty to not bother with it, but be sure to
  firewall that port from everything in the system then (or maybe do it anyway),
  as it's definitely not a good idea to give every process on the machine access
  to that ad-hoc ircd or discord behind it.

- Try: ``/list``, ``/join #control`` and sending "help" there.


Requirements
------------

* `Python 3.7+ <http://python.org/>`_
* `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_
