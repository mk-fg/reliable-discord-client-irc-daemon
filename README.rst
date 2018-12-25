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

  These discord client app id/creds can be - and usually are - hardcoded into
  the application, so that every user don't need to go get them,
  but as I'm probably the only one using this one, don't see much reason to bother.

- In OAuth2 tab there, type https://localhost as a redirect URL,
  select it and "messages.read" scope, copy resulting /api/oauth2/authorize
  URL into ~/.rdircd.ini file like this one::

    [irc]
    password = xyzxyz123

    [discord]
    auth_url = https://discordapp.com/api/oauth2/authorize?client_id=...

  That ini file will be updated with [auth] section by the script to store
  OAuth2 credentials, but it should not touch anything else there.

- Run ./rdircd and it will present an URL for browser and a prompt for
  redirected-to URL after access is granted there - fill that in.

- Connect IRC client to localhost:6667 with the password from ini above.

  Password can be omitted or empty to not bother with it, but be sure to
  firewall that port from every other thing in the system then
  (or maybe do it anyway), as it's definitely not a good idea to give
  every process on the machine access to that ad-hoc ircd or discord.


Requirements
------------

* `Python 3.7+ <http://python.org/>`_
