Reliable Discord-client IRC Daemon (rdircd)
===========================================

Python3/asyncio daemon to present personal discord client as local irc server,
with a list of channels corresponding to ones available on all "connected" discord
channel-hubs (or "servers" as discord confusingly calls these).

One additional "reliable" quirk is that the plan is to have it actually connect
to discord under two separate accounts ("main" and "ghost"), and have these
monitor same channels to detect when stuff posted by the "main" acc doesn't make it,
or any other messages don't get relayed to either of the two,
which is unfortunately an issue that discord API seem to have from time to time.

Under development and not ready for use yet.


Requirements
------------

* `Python 3.7+ <http://python.org/>`_
