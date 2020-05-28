Reliable Discord-client IRC Daemon (rdircd)
===========================================

.. contents::
  :backlinks: none


Description
-----------

Python3/asyncio daemon to present personal Discord_ client as local irc server,
with a list of channels corresponding to ones available on all joined "discord
servers" (group of users/channels with its own theme/auth/rules on discord,
also referred to as `"guilds" in API docs`_).

Purpose is to be able to comfortably use discord via simple text-based IRC client,
and not browser, electron app or anything of the sort.

It's also "reliable" in that it tries hard to confirm message delivery,
notify about any issues in that regard and enforce strict
all-in-same-order-or-nothing posting, which - somewhat surprisingly - other
discord clients seem to be quite sloppy about.

If you have any questions or difficulty, or just want to test this script,
here's an ad-hoc discord for that: https://discord.gg/s2fbWZD

.. _Discord: http://discord.gg/
.. _"guilds" in API docs: https://discordapp.com/developers/docs/resources/guild


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
| Will update this warning blurb if I'll ever get any trouble for using this client myself.
|

Unrelated to this client, but one person reported getting following warning
(2020-01-30) after being reported (by another user) for mentioning that
they're using BetterDiscord_ (which is mostly just custom css theme, afaik):

.. image:: discord-tos-violation-warning.jpg

| Which seem to emphasize "automating" language in ToS.
| So if you don't get even that kind of warning, you're probably safe, but I'm no authority on that.

.. _Bot vs User Accounts: https://discordapp.com/developers/docs/topics/oauth2#bot-vs-user-accounts
.. _BetterDiscord: https://betterdiscord.net/


Features
--------

- Reliable outgoing message ordering and delivery, with explicit notifications
  for issues of any kind.

- Support for both private and public channels, channel ordering.

- Per-server and global catch-all channels to check on general activity.

- Some quirky translation for discord user mentions, see below for specifics.

- Configurable local name aliases.

- Simple and consistent discord to irc guild/channel/user name translation.

  None of these will change after reconnection, channel or server reshuffling,
  etc - translation is mostly deterministic and does not depend on other names.

- Translation for discord mentions, attachments and emojis in incoming msgs.

- Easily accessible backlog via /t (/topic) commands in any channel, e.g. "/t
  log 2h" to show last 2 hours of backlog or "/t log 2019-01-08" to dump backlog
  from that point on to the present, fetching in multiple batches if necessary.

- Own msgs sent thru other means (e.g. browser) will be relayed to irc too,
  maybe coming from a diff nick though, if irc name doesn't match discord-to-irc
  nick translation.

- Full unicode support everywhere.

- IRC protocol is implemented from IRCv3 drafts, but doesn't use any of the
  advanced features, and should be compatible with any clients.

- Extensive protocol and debug logging options, some accessible at runtime via
  #rdircd.debug channel.

- Single python3 script that only requires aiohttp module, trivial to run or
  deploy anywhere.

- Runs in constant ~35M memory footprint on amd64, which is probably more than
  e.g. bitlbee-discord_ but nothing like those leaky browser tabs.

- Easy to tweak and debug without rebuilds, gdb, rust and such.

.. _bitlbee-discord: https://github.com/sm00th/bitlbee-discord


Limitations
-----------

- Only user mentions are translated into discord tags (if enabled and with some
  quirks, see below) - not channels, roles or emojis.

- No support for sending attachments or embeds of any kind - use WebUI for that, not IRC.

  Discord automatically annotates links though, so posting images is as simple as that.

- No discord-specific actions beyond all kinds of reading and sending messages
  to existing channels are supported - i.e. no creating accounts or channels on discord,
  managing roles, bans, timeouts, etc - use WebUI, Harmony_ or proper discord bots.

- Does not track user presence (online, offline, afk, playing game, etc) at all.

- Does not emit user joins/parts events and handles irc /names in a very simple
  way, only listing nicks who used the channel since app startup and within
  irc-names-timeout (1 day by default).

- Completely ignores all non-text-chat stuff in general
  (e.g. voice, user profiles, games library, store, friend lists, etc).

- Does not use or expose discord-server-specific nicknames in any way,
  only global usernames.

- Discord tracks "read_state" server-side, which is not used here in any way -
  triggering history replay is only done manually (/t commands in chans).

- Does not support discord multifactor authentication mode.

- Not the most user-friendly thing, though probably same as IRC itself.

- No TLS mode for IRC - use bouncers like `ZNC <http://znc.in/>`_ for that
  (and for much more than that!).

- Only tested on Linux, probably won't work on OSX/Windows, but idk.

- Has only one known user (me!), so might be only tested and working for that
  single and limited use-case.

- Custom ad-hoc implementation of both discord and irc, not benefitting from any
  kind of exposure and testing on pypi and such wrt bugs and corner-cases.

- No idea if even allowed by Discord ToS - see WARNING section above for more details.


Usage
-----

Requirements
````````````

* `Python 3.7+ <http://python.org/>`_
* `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_

Installation
````````````

Simpliest way might be to use package for/from your linux distribution,
if it is available.

Currently known distro packages (as of 2020-05-17):

- Arch Linux (AUR): https://aur.archlinux.org/packages/rdircd-git/

It should be easy to install this one script and its few dependencies manually
though, e.g. by doing something roughly like this::

  root # useradd -m rdircd
  root # su - rdircd

  rdircd % python -m ensurepip --user
  rdircd % python -m pip install --user aiohttp
  rdircd % curl https://raw.githubusercontent.com/mk-fg/reliable-discord-client-irc-daemon/master/rdircd > rdircd
  rdircd % chmod +x rdircd

  rdircd % ./rdircd --help
   ...to test if it runs...

  rdircd % ./rdircd --conf-dump-defaults
   ...for a full list of all supported options...
  rdircd % nano rdircd.ini
   ...see below for configuration file info/example...

  rdircd % ./rdircd --debug -c rdircd.ini
   ...drop --debug and use init system for a regular daemon...

This assumes that only python3 is installed (see Requirements above) and will
setup script and everything it needs in an rdircd user home directory.

Note that it's generally better to use OS packages for as many steps above as
possible, so that they get updates and avoid such extra local maintenance burden.

Setup and actual usage
``````````````````````

Create configuration file with discord and ircd auth credentials in ~/.rdircd.ini
(see all --conf\* opts wrt these)::

  [irc]
  password = hunter2

  [auth-main]
  email = discord-reg@email.com
  password = discord-password

Note: IRC password can be omitted, but be sure to firewall that port from
everything in the system then (or maybe do it anyway).

| Start rdircd daemon: ``./rdircd --debug``
| (note: if installed from dis

Connect IRC client to "localhost:6667" (see ``./rdircd --conf-dump-defaults``
or -i/--irc-bind option for using diff host/port).

Run ``/list`` to see channels for all joined discord servers/guilds::

  Channel          Users Topic
  -------          ----- -----
  #rdircd.control      0  rdircd: control channel, type "help" for more info
  #rdircd.debug        0  rdircd: debug logging channel, read-only
  #rdircd.monitor      0  rdircd: read-only catch-all channel with messages from everywhere
  #rdircd.monitor.jvpp 0  rdircd: read-only catch-all channel for messages from one discord
  #me.chat.5gupog9fyk  1  me: private chat - SomeUser
  #me.chat.x2s456gl0t  3  me: private chat - some-other-user, another-user, user3
  #jvpp.announcements  0  Server-A: Please keep this channel unmuted
  #jvpp.info           0  Server-A:
  #jvpp.rules          0  Server-A:
  #jvpp.welcome        0  Server-A: Mute unless you like notification spam
  ...
  #axsd.intro          0  Server-B: Server info and welcomes.
  #axsd.offtopic       0  Server-B: Anything goes. Civility is expected.

Notes on information here:

- Short base64 channel prefix is a persistent id of the discord guild that it belongs to.
- Full guild name (e.g. "Server-A") is used as a prefix for every channel topic.
- "#me." is a prefix of discord @me guild, where all private channels are.
- #rdircd.control and #rdircd.debug are special channels, send "help" there for more info.
- There's #rdircd.monitor catch-all channel and guild-specific ones (see notes below).
- Public IRC channel users are transient and only listed/counted if they sent
  something to a channel, as discord has no concept of "joining" for publics.

``/j #axsd.offtopic`` (/join) as you'd do with regular IRC to start shitposting there.
Channels joins/parts in IRC side do not affect discord in any way.

Run ``/t`` (/topic) command to show more info on channel-specific commands,
e.g. ``/t log`` to fetch and replay backlog starting from last event before last
rdircd shutdown, ``/t log list`` to list all activity timestamps that rdircd tracks,
or ``/t log 2h`` to fetch/dump channel log for/from specific time(stamp/span)
(iso8601 or a simple relative format).

Discord-global commands are available in #rdircd.control channel, #rdircd.debug
chan can be used to tweak various logging and inspect daemon state and protocols
more closely, send "help" there to list available commands.


Misc Feature Info
-----------------

| Notes on various optional and less obvious features are collected here.
| See "Usage" section for a more general information.

Multiple Config Files
`````````````````````

Multiple ini files can be specified with -c option, overriding each other in sequence.

Last one will be updated wrt [state], token= and similar runtime stuff,
so it can be useful to specify persistent config with auth and options,
and separate (initially empty) one for such dynamic state.

| E.g. ``./rdircd -c config.ini -c state.ini`` will do that.
| ``--conf-dump`` can be added to print resulting ini assembled from all these.
| ``--conf-dump-defaults`` flag can be used to list all options and their defaults.
|

Frequent state timestamp updates are done in-place (small fixed-length values),
but checking ctime before writes, so should be safe to tweak any of these files
anytime anyway.

Channel Commands
````````````````

| In special channels like #rdircd.control and #rdircd.debug: send "h" or "help".
| All discord channels - send "/t" or "/topic".

Local Name Aliases
``````````````````

Can be defined in the config file to replace hash-based IDs with something
easily readable::

  [aliases]
  guild.jvpp = game-X

(to turn e.g. #jvpp.info into #game-X.info)

Currently only implemented for guild IDs in IRC channel names.

#rdircd.monitor channels
````````````````````````

#rdircd.monitor can be used to check on activity from all connected servers -
gets all messages, prefixed by the relevant irc channel name.

#rdircd.monitor.guild (where "guild" is a hash or alias, see above)
is a similar catch-all channels for specific discord server/guild.

They are currently created on-first-message, so might not be listed initially,
but can be joined anytime (same as with any other channels).
Joining #rdircd.monitor.me can be useful in particular to monitor any private
chats and messages for the account.

Messages in these channels are limited to specific length/lines
to avoid excessive flooding of these by multi-line msgs.

"len-monitor" and "len-monitor-lines" parameters under "[irc]" config section
can be used to control max length for these,
see ``./rdircd --conf-dump-defaults`` output for their default values.

Private messages and friends
````````````````````````````

Discord private messages create and get posted to channels in "me" server/guild,
same as they do in discord webui, and can be interacted with in the same way as
any other guild/channels (list, join/part, send/recv msgs, etc).

Join #rdircd.monitor.me (or #rdircd.monitor, see above) to get all new
msgs/chats there, as well as relationship change notifications (friend
requests/adds/removes) as notices.

Accepting friend requests and adding/removing these can be done via regular
discord webui and is not implemented in this client in any special way.

Discord user mentions
`````````````````````

| These are ``@username`` tags, designed to alert someone to direct-ish message.
| rdircd translates whatever matches ``msg-mention-re`` regexp conf-option into them.

Default value for it should look like this::

  [discord]
  msg-mention-re = (?:^|\s)(@)(?P<nick>[^\s,;@+]+)

Which would match any word-like space- or punctuation-separated ``@nick``
mention in sent lines.

Regexp (`python "re" syntax`_) must have named "nick" group with
nick/username lookup string, which will be replaced by discord mention tag,
and all other capturing groups (i.e. ones without ``?:``) will be stripped
(like ``@`` in above regexp).

Default regexp above should still allow to send e.g. ``\@something`` to appear
non-highlighted in webapp (and without ``\`` due to markdown), as it won't be
matched by ``(?:^|\s)`` part due to that backslash prefix.

As another example, to have classic irc-style highlights at the start of the
line, regexp like this one can be used::

  msg-mention-re = ^(?P<nick>[^\s,;@+]+)(:)

And should translate e.g. ``mk-fg: some msg`` into ``@mk-fg some msg``
(with @-part being mention-tag).

To ID specific discord user, "nick" group will be used in following ways:

- Case-insensitive match against all recent guild-related irc names
  (message authors, reactions, private channel users, etc).

- Lookup unique name completion by prefix, same as in webui after @.

- If no cached or unique match found - error notice will be issued
  and message not sent.

Such strict behavior is designed to avoid any unintentional mis-translations,
and highlighting wrong person should generally only be possible via misspelling.

Related ``msg-mention-re-ignore`` option (regexp to match against full capture
of pattern above) can also be used to skip some non-mention things from being
treated as such, that'd otherwise be picked-up by first regexp, stripping
capturing groups from them too, which can be used to e.g. undo escaping.

Set ``msg-mention-re`` to an empty value to disable all this translation entirely.

Note that discord user lists can be quite massive (10K+ users), are not split
by channel, and are not intended to be pre-fetched by the client, only queried
for completions or visible parts, which doesn't map well to irc, hence all this magic.

.. _python "re" syntax: https://docs.python.org/3/library/re.html#regular-expression-syntax

Lookup Discord IDs
``````````````````

Mostly useful for debugging - /who command can resolve specified ID
(e.g. channel_id from protocol logs) to a channel/user/guild info:

- ``/who #123456`` - find/describe channel with id=123456.
- ``/who @123456`` - user id lookup.
- ``/who %123456`` - guild id info.

All these ID values are unique for discord within their type.

Channel name disambiguation
```````````````````````````

Discord name translation is "mostly" deterministic due to one exception -
channels with exactly same name within same server/guild, which discord allows.

Only when there is a conflict, these are suffixed by .1, .2, etc in alpha-sort
order of their (constant) IDs, so same combination of channels will retain same
suffixes, regardless of any ordering quirks.

Renaming conflicting channels will rename IRC chans to unsuffixed ones as well.

Note that when channels are renamed (incl. during such conflicts), IRC notice
lines about it are always issued in both affected channels and relevant
#rdircd.monitor channels.

WARNING :: Session/auth rejected unexpectedly - disabling connection
````````````````````````````````````````````````````````````````````

This should happen by default when discord gateway responds with op=9
"invalid session" event to an authentication attempt,
not reconnecting after that, as presumably it'd fail in the same way anyway.

This would normally mean that authentication with the discord server has failed,
but on (quite frequent) discord service disruptions, gateway also returns that
opcode for all logins after some timeout, presumably using it as a fallback
when failing to access auth backends.

This can get annoying fast, as one'd have to manually force reconnection when
discord itself is in limbo.

If auth data is supposed to be correct, can be fixed by setting
``ws-reconnect-on-auth-fail = yes`` option in ``[discord]`` ini section,
which will force client to keep reconnecting regardless.

asyncio ERROR :: Fatal read error on socket transport
`````````````````````````````````````````````````````

Rarely this error might pop-up randomly, when websocket connection is patchy::

  asyncio ERROR :: Fatal read error on socket transport
  protocol: <asyncio.sslproto.SSLProtocol object at 0x7f057da99080>
  transport: <_SelectorSocketTransport fd=9 read=polling write=<idle, bufsize=0>>
  Traceback (most recent call last):
    File "/usr/lib/python3.7/asyncio/selector_events.py", line 801, in _read_ready__data_received
      data = self._sock.recv(self.max_size)
  TimeoutError: [Errno 110] Connection timed out

It's a problem in python3 asyncio, as described in `Python Issue 34148`_ and `PR#11576`_.

.. _Python Issue 34148: https://bugs.python.org/issue34148
.. _PR#11576: https://github.com/python/cpython/pull/11576

Captcha-solving is required to login for some reason
````````````````````````````````````````````````````

Don't know why or when it happens, but was reported by some users in this and
other similar discord clients - see `issue-1`_ here and links in there.

Fix is same as with bitlbee-discord_ - login via browser, maybe from the same
IP Address, and put auth token extracted from this browser into configuration
ini file's [auth-main] section, e.g.::

  [auth-main]
  token = ...

See "Usage" in README of bitlbee-discord_ (scroll down on that link) for how to
extract this token from various browsers.

Note that you can use multiple configuration files (see -c/--conf option) to specify
this token via separate file, generated in whatever fashion, in addition to main one.

Extra ``token-manual = yes`` option can be added in that section to never
try to request, update or refresh this token automatically in any way.
Dunno if this option is needed, or if such captcha-login is only required once,
and later automatic token requests/updates might work (maybe leave note on
`issue-1`_ if you'll test it one way or the other).

Never encountered this problem myself so far.

.. _issue-1: https://github.com/mk-fg/reliable-discord-client-irc-daemon/issues/1

Anything unknown or unexpected
``````````````````````````````

Can be seen in #rdircd.debug channel with warning/error level, as well as logged to stderr.

These should not normally occur though, unless there's a bug or - more likely -
missing handling for some new/uncommon events (either can be reported as a
github issue), so joining/monitoring either of these sources is recommended.


Links
-----

Other third-party Discord clients that I'm aware of atm (2020-05-07),
in no particular order.

IRC-translation clients (like this one):

- bitlbee_ + bitlbee-discord_ - similar IRC interface
- bitlbee_ + libpurple (from Pidgin_) - diff discord implementation from above
- ircdiscord_ - Go client proxy, based on same lib as gtkcord_ and 6cord_

Graphical UI (GUI) clients:

- Pidgin_ - popular cross-platform client, its libpurple can be used from bitlbee_ as well
- gtkcord_ - liteweight Go/GTK3 client, also works on linuxy phones (like PinePhone_)
- Ripcord_ - cross-platform proprietary shareware client, also supports slack

Web UI (in-browser) clients:

- BetterDiscord_ - alternative in-browser web interface/client (see also BandagedBD_ fork)
- Powercord_ - privacy and client extension oriented mod/framework
- Glasscord_ - discord client tweak for transparency and nicer looks
- EnhancedDiscord_ (`joe27g/EnhancedDiscord`_) - JS plugin framework for extra client functionality

Terminal UI (TUI, ncurses) clients:

- Cordless_ - fairly mature Go TUI client
- 6cord_ - Go client, seem to be deprecated atm in favor of gtkcord_
- Terminal-Discord_ - minimal JS/node terminal client
- `Discord Terminal`_ - customizable JS/node client with IRC layout and Windows OS support
- Discurses_ - python urwid/curses client
- Discline_ - another python client with typical IRC looks, seem to be broken atm

Command-line clients:

- Harmony_ - tool for discord account manipulation - e.g. create, change settings, accept invites, etc

Not an exhaustive list by any means.

.. _bitlbee: https://www.bitlbee.org/
.. _Pidgin: https://pidgin.im/
.. _ircdiscord: https://github.com/tadeokondrak/ircdiscord/
.. _gtkcord: https://github.com/diamondburned/gtkcord3/
.. _PinePhone: https://www.pine64.org/pinephone/
.. _Ripcord: https://cancel.fm/ripcord/
.. _BandagedBD: https://github.com/rauenzi/BetterDiscordApp
.. _Powercord: https://powercord.dev/
.. _Glasscord: https://github.com/AryToNeX/Glasscord
.. _EnhancedDiscord: https://enhanceddiscord.com/
.. _joe27g/EnhancedDiscord: https://github.com/joe27g/EnhancedDiscord
.. _6cord: https://gitlab.com/diamondburned/6cord/
.. _Cordless: https://github.com/Bios-Marcel/cordless
.. _Terminal-Discord: https://github.com/xynxynxyn/terminal-discord
.. _Discord Terminal: https://github.com/cloudrex/discord-term
.. _Discurses: https://github.com/topisani/Discurses
.. _Discline: https://github.com/MitchWeaver/Discline
.. _Harmony: https://github.com/nickolas360/harmony


API and Implementation Notes
----------------------------

Note: only using this API here, only going by public info, can be wrong,
and would appreciate any updates/suggestions/corrections via open issues.

Last updated: 2020-05-23

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

- Some events on gateway websocket are undocumented, maybe due to lag of docs
  behind implementation, or due to them not being deemed that useful to bots, idk.

- Discord allows channels (and probably users) to have exactly same name, which is not
  a big deal for users (due to one-way translation), but have to be disambiguated for channels.

- Discord status page with something like 99.98% API/gateway uptimes is
  completely useless, as it only seem to track frontend accessibility via tcp connections,
  and it's almost always fails are backends, timing-out logins and returning error opcodes.

  At least in my experience so far, discord servers seem to fail like that for a
  few minutes to an hour or two pretty much every other week.

- Gateway websocket `can use zlib compression`_, which makes inspecting protocol in
  browser devtools a bit inconvenient. `gw-ws-har-decode.py <gw-ws-har-decode.py>`_
  helper script in this repo can be used to decompress/decode websocket messages saved
  from chromium-engine browser devtools (pass -h/--help option for info on how to do it).

.. _can use zlib compression: https://discord.com/developers/docs/topics/gateway#encoding-and-compression
