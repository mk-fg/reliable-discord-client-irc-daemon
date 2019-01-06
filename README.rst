Reliable Discord-client IRC Daemon (rdircd)
===========================================

Python3/asyncio daemon to present personal discord client as local irc server,
with a list of channels corresponding to ones available on all joined "discord
servers" (group of users/channels with its own theme/auth/rules on discord,
also referred to as "guilds" in API docs).

Purpose is to be able to comfortably use discord via simple text-based IRC client,
and not browser, electron app or anything of the sort.

One additional "reliable" quirk is that the plan is to have it actually connect
to discord under two separate accounts ("main" and "ghost"), and have these
monitor same channels to detect when stuff posted by the "main" acc doesn't make it,
or any other messages don't get relayed to either of the two,
which is unfortunately an issue that either discord api or other clients that
I've used seem to have from time to time.

Or maybe just tracking MESSAGE_ACK events would be enough, if that's a thing.

Under development and not ready for use yet.


WARNING
-------

While I wouldn't call this app a "bot" exactly - intent here is not to post any
automated messages or scrape anything - Discord staff might, and Discord
requires bots to use special second-class API and for every account of such to
be approved by admins on every connected discord server/guild, making it
effectively unusable for a random non-admin user.

As this app does not present itself as a "bot" and doesn't use bot-specific
endpoints, if Discord staff would classify it as such, it might result in
blocking of user account(s).

See `Bot vs User Accounts`_ in dev docs for more information on the distinction.

.. _Bot vs User Accounts: https://discordapp.com/developers/docs/topics/oauth2#bot-vs-user-accounts


Requirements
------------

* `Python 3.7+ <http://python.org/>`_
* `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_


API and Implementation Notes
----------------------------

Note: only using this API here, only going by public info, can be wrong,
and would appreciate any updates/suggestions/corrections via open issues.

Last updated: 2019-01-02

- Discord API docs don't seem to cover "full-featured client" use-case,
  which likely means that such use is not officially supported or endorsed.

  See WARNING section above for what it might potentially imply.

- Auth uses undocumented /api/auth/login endpoint for getting "token" value for
  email/password, which is not OAuth2 token and is usable for all other endpoints
  (e.g. POST URLs, Gateway, etc) without any prefix in HTTP Authorization header.

  Found it being used in other clients, and dunno if there's any other way to
  authorize non-bot on e.g. Gateway websocket - only documented auth is OAuth2,
  and it doesn't seem to allow that.

  Being apparently undocumented and available since the beginning,
  guess it might be heavily deprecated by now and go away at any point in the future.

- Some events coming from websocket gateway are undocumented, maybe due to lag
  of docs behind implementation, or due to them not being deemed that useful to bots, idk.
