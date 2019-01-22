Reliable Discord-client IRC Daemon (rdircd)
===========================================

.. contents::
  :backlinks: none


Description
-----------

Python3/asyncio daemon to present personal Discord_ client as local irc server,
with a list of channels corresponding to ones available on all joined "discord
servers" (group of users/channels with its own theme/auth/rules on discord,
also referred to as "guilds" in API docs).

Purpose is to be able to comfortably use discord via simple text-based IRC client,
and not browser, electron app or anything of the sort.

It's also "reliable" in that it tries hard to confirm message delivery,
notify about any issues in that regard and enforce strict
all-in-same-order-or-nothing posting, which - somewhat surprisingly - other
discord clients seem to be quite sloppy about.

.. _Discord: http://discord.gg/


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

| See `Bot vs User Accounts`_ in dev docs for more information on the distinction.
| Will update this warning blurb if I'll ever get banned for using this client myself.

.. _Bot vs User Accounts: https://discordapp.com/developers/docs/topics/oauth2#bot-vs-user-accounts


Features
--------

- Reliable outgoing message ordering and delivery, with explicit notifications
  for issues of any kind.

- Support for both private and public channels, channel ordering.

- Simple and consistent discord to irc guild/channel/user name translation.

  None of these will change after reconnection, channel or server reshuffling,
  etc - translation is fully deterministic and does not depend on other names.

- Translation for discord mentions, attachments and emojis.

- Easily accessible backlog via /t (/topic) commands in any channel, e.g. "/t
  log 2019-01-08" to dump backlog from that point on to the present, using as
  many API requests as necessary (no message count limits).

- Full unicode support everywhere.

- IRC protocol is implemented from IRCv3 drafts, but doesn't use any of the
  advanced features, and should be compatible with any clients.

- Extensive protocol and debug logging options, some accessible at runtime via
  #debug channel.

- Single python3 script that only requires aiohttp module, trivial to run or
  deploy anywhere.

- Runs in constant ~35M memory footprint on amd64, which is probably more than
  e.g. `bitlbee-discord <https://github.com/sm00th/bitlbee-discord>`_ but nothing
  like those leaky browser tabs.

- Easy to tweak and debug without rebuilds, gdb, rust and such.


Limitations
-----------

- Won't /q or ping on new direct/private messages in any way yet, but will
  probably implement that at some point.

- No support for sending attachments or embeds of any kind - use WebUI for that,
  not IRC.

  Discord automatically annotates links though, so posting images is as simple as that.

- No discord-specific actions beyond all kinds of reading and sending messages
  to existing channels are supported - i.e. no creating new channels on discord,
  managing roles, bans, timeouts, etc - use proper discord bots for that.

- Does not track user presence (online, offline, afk, playing game, etc) at all.

- Does not emit user joins/parts events and handles irc /names in a very simple
  way, only listing nicks who used the channel since app startup and within
  irc-names-timeout (1 day by default).

- Completely ignores all non-text-chat stuff in general
  (e.g. voice, user profiles, games library, store, friend lists, etc).

- Does not support discord multifactor authentication mode.

- Not the most user-friendly thing, though probably same as IRC itself.

- No TLS mode for IRC - use bouncers like `ZNC <http://znc.in/>`_ for that
  (and for much more than that!).

- Only tested on Linux, probably won't work on OSX/Windows, but idk.

- Has only one user (me!), so might be only tested and working for that single
  and limited use-case.

- Custom ad-hoc implementation of both discord and irc, not benefitting from any
  kind of exposure and testing on pypi and such.

  Though mostly due to both having rather trivial text-based protocols, simplier
  than module APIs and with no extra crap in the middle.

- No idea if even allowed by Discord ToS - see WARNING section above for more details.


Usage
-----

Install script dependencies (see Requirements section below)::

  % pip3 install --user aiohttp

Create configuration file with discord and ircd auth credentials in ~/.rdircd.ini
(see all the --conf\* opts wrt these)::

  [irc]
  password = hunter2

  [auth-main]
  email = discord-reg@email.com
  password = discord-password

Note: IRC password can be omitted, but be sure to firewall that port from
everything in the system then (or maybe do it anyway).

Start rdircd daemon: ``./rdircd --debug``

Connect IRC client to "localhost:6667" (see ``./rdircd --conf-dump-defaults``
or -i/--irc-bind option for using diff host/port).

Run ``/list`` to see channels for all joined discord servers/guilds::

  Channel          Users Topic
  -------          ----- -----
  #control            0  rdircd: control channel, type "help" for more info
  #debug              0  rdircd: debug logging channel, read-only
  #me.SomeUser        1  me: private chat - SomeUser
  #me.some-other-user 1  me: private chat - some-other-user
  #jvPp.announcements 0  Server-A: Please keep this channel unmuted
  #jvPp.info          0  Server-A:
  #jvPp.rules         0  Server-A:
  #jvPp.welcome       0  Server-A: Mute unless you like notification spam
  ...
  #aXsd.intro         0  Server-B: Server info and welcomes.
  #aXsd.offtopic      0  Server-B: Anything goes. Civility is expected.

Notes on information here:

- Short base64 channel prefix is a persistent id of the discord guild that it belongs to.
- Full guild name (e.g. "Server-A") is used as a prefix for every channel topic.
- "#me." is a prefix of discord @me guild, where all private channels are.
- #control and #debug are special channels, send "help" there for more info.
- Public IRC channel users are transient and only listed/counted if they sent
  something to a channel, as discord has no concept of "joining" for publics.

``/j #aXsd.offtopic`` (/join) as you'd do with regular IRC to start shitposting there.

Run ``/t`` (/topic) command to show more info on channel-specific commands,
e.g. ``/t log`` to fetch and replay backlog since last rdircd shutdown time,
``/t log list`` to list all the activity timestamps that rdircd tracks,
or ``/t log 2019-01-08`` to fetch/dump channel log since specific date/time
(in iso8601 format).

Discord-global commands are available in #control channel,
send "help" here for information on all of these.


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

- Sent message delivery confirmation is done by matching unique "nonce" value in
  MESSAGE_CREATE event from gateway websocket with one sent out to REST API.

  All messages are sent out in strict sequence (via one queue), with synchronous
  waiting on confirmation, aborting whole queue if first one fails to be delivered,
  with notices for each failed/discarded msg.

  This is done to ensure that all messages either arrive in the same strict
  order they've been sent or not posted at all.

- Some events coming from websocket gateway are undocumented, maybe due to lag
  of docs behind implementation, or due to them not being deemed that useful to bots, idk.
