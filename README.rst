Reliable Discord-client IRC Daemon (rdircd)
===========================================

.. contents::
  :backlinks: none


Description
-----------

rdircd is a daemon that allows using a personal Discord_ account through an IRC_ client.

It translates all private chats and public channels/threads on "discord servers"
into channels on an IRC server that it creates and that you can connect to using
regular IRC client, instead of a browser or electron app.

"reliable" is in the name because one of the initial goals was to make it confirm
message delivery and notify about any issues in that regard, which was somewhat
lacking in other similar clients at the time.

| There's an IRC channel to talk about the thing - join `#rdircd at libera.chat`_.
| IRC URL: ircs://irc.libera.chat/rdircd (github refuses to make ircs:// links)

See also Links_ section below for rarely-updated list of other alternative clients.

Repository URLs:

- https://github.com/mk-fg/reliable-discord-client-irc-daemon
- https://codeberg.org/mk-fg/reliable-discord-client-irc-daemon
- https://fraggod.net/code/git/reliable-discord-client-irc-daemon

Last one has git-notes with todo list and such at the default ref for those.

.. _Discord: http://discord.gg/
.. _IRC: https://en.wikipedia.org/wiki/Internet_Relay_Chat
.. _#rdircd at libera.chat: https://web.libera.chat/?channels=#rdircd


WARNING
-------

While I wouldn't call this app a "bot" or "automating standard user accounts" -
intent here is not to post any automated messages or scrape anything - pretty sure
Discord staff considers all third-party clients to be "bots", and requires them to
use special second-class API (see `Bot vs User Accounts`_ section in API docs),
where every account has to be separately approved by admins on every connected
discord server/guild, making it effectively unusable for a random non-admin user.

This app does not present itself as a "bot" and does not use bot-specific endpoints,
so using it can result in account termination if discovered.

See also `More info on third-party client blocking`_ section below.

You have been warned! :)

.. _Bot vs User Accounts:
  https://discord.com/developers/docs/topics/oauth2#bot-vs-user-accounts


Features
--------

- Reliable outgoing message ordering and delivery, with explicit notifications
  for detected issues of any kind.

- Support for both private and public channels, channel ordering, threads,
  forums, except for creating any new ones of these.

- Per-server and global catch-all channels to track general activity.

- Limited translation for using discord user mentions in sent messages,
  edits and deletions.

- Configurable local name aliases/renames, outgoing message blocks/replacements,
  regexp-filtering for received messages.

- Support for limited runtime reconfiguration via #rdircd.control channel.

- Simple and consistent discord to irc guild/channel/user name translation.

  None of these will change after reconnection, channel or server reshuffling,
  etc - translation is mostly deterministic and does not depend on other names.

- Translation for discord mentions, replies, attachments, stickers and emojis
  in incoming msgs, other events, basic annotations for some embedded links.

- Easily accessible backlog via /topic (/t) commands in any channel, e.g. "/t
  log 2h" to show last 2 hours of backlog or "/t log 2019-01-08" to dump backlog
  from that point on to the present, fetching in multiple batches if necessary.

- Messages sent through other means (e.g. browser) will be relayed to irc too,
  maybe coming from a diff nick though, if irc name doesn't match discord-to-irc
  nick translation.

- Full unicode support/use everywhere.

- IRC protocol is implemented from IRCv3 docs, but doesn't use any non-RFC stuff,
  so should be compatible with any old clients. Optional TLS wrapping.

- Extensive protocol and debug logging options, some accessible at runtime via
  #rdircd.debug channel.

- Single python3 script that only requires aiohttp module, trivial to run or
  deploy anywhere.

- Runs in relatively stable ~40M memory footprint on amd64, which is probably
  more than e.g. bitlbee-discord_, but better than those leaky browser tabs.

- Easy to tweak and debug without rebuilds, gdb, rust and such.

.. _bitlbee-discord: https://github.com/sm00th/bitlbee-discord


Limitations
-----------

- Only user mentions sent from IRC are translated into discord tags
  (if enabled and with some quirks, see below) - not channels, roles, stickers,
  components or emojis.

- No support for sending attachments or embeds of any kind - use WebUI for that, not IRC.

  Discord automatically annotates links though, so posting media is as simple as that.

- No discord-specific actions beyond all kinds of reading and sending messages
  to existing channels are supported - i.e. no creating accounts or channels on discord,
  managing roles, invites, bans, timeouts, etc - use WebUI, Harmony_ or proper discord bots.

- Creating new private chats and channel/forum threads is not supported.

  For private chats, it might be even dangerous to support - see `More info on
  third-party client blocking`_ section below for details.

- Does not track user presence (online, offline, afk, playing game, etc) at all.

- Does not emit user joins/parts events and handles irc /names in a very simple
  way, only listing nicks who used the channel since app startup and within
  irc-names-timeout (1 day by default).

- Completely ignores all non-text-chat stuff in general
  (e.g. voice, user profiles, games library, store, friend lists, etc).

- Discord tracks "read_state" server-side, which is not used here in any way -
  triggering history replay is only done manually (/t commands in chans),
  so can sometimes be easy to miss on quiet reconnects.

- Does not support discord multifactor authentication mode, but manual-token
  auth can probably work around that - see note on captchas below.

- `Slash commands`_ (for bots) are not supported in any special way,
  but you can probably still send them, if IRC client will pass these through.

- Not the most user-friendly thing, though probably same as IRC itself.

- I only run it on Linux, so it's unlikely to "just work" on OSX/Windows, but idk.

- Custom ad-hoc implementation of both discord and irc, not benefitting from any
  kind of exposure and testing on pypi and such wrt compatibility, bugs and corner-cases.

- Seem to be against Discord guidelines to use it - see WARNING section above for more details.

.. _Slash commands: https://discord.com/developers/docs/interactions/slash-commands


Usage
-----

Requirements
````````````

* `Python 3.8+ <http://python.org/>`_
* `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_

Installation
````````````

Simpliest way might be to use package for/from your linux distribution,
if it is available.

Currently known distro packages (as of 2020-05-17):

- Arch Linux (AUR): https://aur.archlinux.org/packages/rdircd-git/

There's also a Dockerfile_ and docker-compose.yml_ for running this
in a docker/podman or some other OCI-compatible containerized environment.

Should be easy to install one script and its few dependencies manually as well,
as described in the rest of this section below.

On debian/ubuntu, installing dependencies can be done with this one command::

  # apt install --no-install-recommends python3-minimal python3-aiohttp

Other linux distros likely have similar packages as well, and I'd recommend
trying to use these as a first option, so that they get updates and to avoid
extra local maintenance burden, and only fallback to installing module(s) via
"pip" if that fails.

On any arbitrary distro with python (python3) installed, using pip/venv to
install aiohttp module (and its deps) to unprivileged "rdircd" user's home dir
might work (which is also used to run rdircd in the next example below),
but ignore this if you've already installed it via OS package manager or such::

  root # useradd -m rdircd
  root # su - rdircd

  ## Option 1: use venv to install dependencies into "_venv" dir

  rdircd % python3 -m venv _venv
  rdircd % ./_venv/bin/pip install aiohttp

  ## Option 2: install pip (if missing) and use it directly

  rdircd % python3 -m ensurepip --user
  rdircd % python3 -m pip install --user aiohttp

After requirements above are installed, script itself can be fetched
from this repository and run like this::

  ## Ignore "useradd" if you've already created a user when running "pip" above
  root # useradd -m rdircd
  root # su - rdircd

  ## If using "venv" install example above - load its env vars
  # Or alternatively run script via "./_venv/bin/python rdircd ..." command line
  rdircd % source ./_venv/bin/activate

  rdircd % curl https://raw.githubusercontent.com/mk-fg/reliable-discord-client-irc-daemon/master/rdircd > rdircd
  rdircd % chmod +x rdircd

  rdircd % ./rdircd --help
   ...to test if it runs...

  rdircd % ./rdircd --conf-dump-defaults
   ...for a full list of all supported options with some comments...
  rdircd % nano rdircd.ini
   ...see below for configuration file info/example...

  rdircd % ./rdircd --debug -c rdircd.ini
   ...drop --debug and use init system for a regular daemon...

For setting up daemon/script to run on OS boot, rdircd.service_ systemd unit file
can be used in most Linux environments (edit ExecStart= options and paths there),
or otherwise probably via init.d script, or maybe in "screen" session as a
last resort ad-hoc option.
Make sure it runs as e.g. "rdircd" user created in snippet above, not as root.

.. _Dockerfile: Dockerfile
.. _docker-compose.yml: docker-compose.yml
.. _rdircd.service: rdircd.service

Setup and actual usage
``````````````````````

Create configuration file with discord and ircd auth credentials in ~/.rdircd.ini
(see all --conf\* opts wrt these)::

  [irc]
  password = hunter2

  [auth]
  email = discord-reg@email.com
  password = discord-password

Note: IRC password can be omitted, but make sure to firewall that port from
everything in the system then (or maybe do it anyway).

If you set password though, maybe do not use IRC ``password=`` option like above,
and use ``password-hash=`` and ``-H/--conf-pw-scrypt`` to generate it instead.
Either way, make sure to use that password when configuring connection to this
server in the IRC client as well.

Start rdircd daemon: ``./rdircd --debug``

Connect IRC client to "localhost:6667" - default listen/bind host and port.

(see ``./rdircd --conf-dump-defaults`` or corresponding CLI ``-i/--irc-bind`` /
``-s/--irc-tls-pem-file`` options for binding on different host/port and TLS
socket wrapping, for non-localhost connections)

Run ``/list`` to see channels for all joined discord servers/guilds::

  Channel           Users Topic
  -------           ----- -----
  #rdircd.control       1  rdircd: control channel, type "help" for more info
  #rdircd.debug         1  rdircd: debug logging channel, read-only
  #rdircd.monitor       1  rdircd: read-only catch-all channel with messages from everywhere
  #rdircd.leftover      1  rdircd: read-only channel for any discord messages in channels ...
  #rdircd.monitor.jvpp  1  rdircd: read-only catch-all channel for discord [ Server-A ]
  #rdircd.leftover.jvpp 1  rdircd: read-only msgs for non-joined channels of discord [ Server-A ]
  ...
  #me.chat.SomeUser     1  me: private chat - SomeUser
  #me.chat.x2s456gl0t   3  me: private chat - some-other-user, another-user, user3
  #jvpp.announcements   1  Server-A: Please keep this channel unmuted
  #jvpp.info            1  Server-A:
  #jvpp.rules           1  Server-A:
  #jvpp.welcome         1  Server-A: Mute unless you like notification spam
  ...
  #axsd.intro           1  Server-B: Server info and welcomes.
  #axsd.offtopic        1  Server-B: Anything goes. Civility is expected.

Notes on information here:

- Short base64 channel prefix is a persistent id of the discord guild that it belongs to.
- Full guild name (e.g. "Server-A") is used as a prefix for every channel topic.
- "#me." is a prefix of discord @me guild, where all private channels are.
- #rdircd.control and #rdircd.debug are special channels, send "help" there for more info.
- There's #rdircd.monitor catch-all channel and guild-specific ones (see notes below).
- #rdircd.leftover channels are like #rdircd.monitor, but skip msgs from already-joined channels.
- Public IRC channel users are transient and only listed/counted if they sent
  something to a channel, as discord has no concept of "joining" for publics.
- Everything in that /list and everything used to talk through this app are IRC
  channels (with #, that you /join), it doesn't use /q or /msg pretty much anywhere.
- Channels always list at least 1 user, to avoid clients hiding ones with 0.

``/j #axsd.offtopic`` (/join) as you'd do with regular IRC to start shitposting there.
Channels joins/parts in IRC side do not affect discord in any way.

Run ``/topic`` (often works as ``/t``) irc-command to show more info on
channel-specific commands, e.g. ``/t log`` to fetch and replay backlog starting
from last event before last rdircd shutdown, ``/t log list`` to list all
activity timestamps that rdircd tracks, or ``/t log 2h`` to fetch/dump channel
log for/from specific time(stamp/span) (iso8601 or a simple relative format).

Daemon control/config commands are available in #rdircd.control channel,
#rdircd.debug chan can be used to tweak various logging and inspect daemon state
and protocols more closely, send "help" there to list available commands.

For broad outline of various supported configuration settings,
see `rdircd.defaults.ini`_ file (output of ``./rdircd --conf-dump-defaults``),
and more on particular uses of those below.

.. _rdircd.defaults.ini: rdircd.defaults.ini


Misc Feature Info
-----------------

| Notes on various optional and less obvious features are collected here.
| See "Usage" section for a more general information.

Multiple Config Files
`````````````````````

Multiple ini files can be specified with -c option, overriding each other in sequence.

Last one will be updated wrt [state], token= and similar runtime stuff,
as well as any values set via #rdircd.control channel commands,
so it can be useful to specify persistent config with auth and options,
and separate (initially empty) one for such dynamic state.

| E.g. ``./rdircd -c config.ini -c state.ini`` will do that.
| ``--conf-dump`` can be added to print resulting ini assembled from all these.
| ``--conf-dump-defaults`` flag can be used to list all options and their defaults.
|

Frequent state timestamp updates are done in-place (small fixed-length values),
but checking ctime before writes, so should be safe to edit any of these files
manually anytime anyway.

Sending SIGHUP to the script or "reload" command in control-channel should
load and apply values from all config files in the same order.
Note that such operation won't reset any values missing in files to their
defaults, only apply stuff explicitly set there on top of the current config.

Channel Commands
````````````````

| In special channels like #rdircd.control and #rdircd.debug: send "h" or "help".
| All discord channels - send "/t" or "/topic".

#rdircd.monitor and #rdircd.leftover channels
`````````````````````````````````````````````

#rdircd.monitor can be used to see activity from all connected servers -
gets all messages, prefixed by the relevant irc channel name.

#rdircd.monitor.guild (where "guild" is a hash or alias, see above)
is a similar catch-all channels for specific discord server/guild.

#rdircd.monitor.me can be useful, for example, to monitor any private chats
and messages for discord account (see also `Auto-joining channels`_ example).

#rdircd.leftover and similar #rdircd.leftover.guild channels are like monitor
channels, but skip messages from any channels that IRC client have JOIN-ed,
including e.g. ``/join #rdircd.leftover.game-x`` hiding that "game-x" discord
msgs from global catch-all #rdircd.leftover, but not counting #rdircd.monitor
channels (i.e. joining them doesn't affect "leftover" ones in any way).

Configuration file also has [unmonitor] section for an optional list
of channel-names to ignore in monitor/leftover channels, for example::

  [unmonitor]
  # All filters are applied to channel names and are case-insensitive
  Ignore this particular "bot-commands" channel = game-X.bot-commands
  skip forum threads in "game-X" guild = glob:game-X.forum.=*
  "wordle" threads in any guild (and chans ending in .wordle) = glob:*.wordle
  Don't show threads in any forum-like channels = re:^[^.]+\.(forum|discuss)\.=.*

Keys (as in part before "=") in such config section are ignored, and can be
anything, e.g. comments explaining the patterns (like in example above), while
values are either exact channel names (with discord prefix, optional #-prefix),
or a "glob:"/"re:"-prefixed glob / regexp pattern (`shell-like globs`_ or
`python regexps`_), written as ``<some-key/comment> = glob:<wildcard-pattern>``
or ``<some-key/comment> = re:<regexp-pattern>`` lines - see examples just above.

Channel names matched by those filters will be dropped from monitor-channels,
so this can be used to define a list of spammy things that you don't care about
and don't want to see even there.

"unmonitor" (or "um") command in #rdircd.control can add/remove such filters
on-the-fly anytime.

Messages in monitor-channels are limited to specific length/lines,
to avoid excessive flooding by long and/or multi-line msgs.
"len-monitor" and "len-monitor-lines" parameters under "[irc]" config
section can be used to control these limits,
see `"./rdircd --conf-dump-defaults" output`_ for their default values.
There are also options to change name format of monitor channels.

.. _shell-like globs: https://docs.python.org/3/library/fnmatch.html
.. _python regexps: https://docs.python.org/3/library/re.html
.. _"./rdircd --conf-dump-defaults" output: rdircd.defaults.ini

People's names on discord
`````````````````````````

On IRC, everyone has one name, but that's `not the case with Discord`_,
where each user can have following names:

- ``login`` - discord "username", uniquely identifying every user.
- ``display`` - "display name" set by the user in discord account settings, not unique.
- ``nick`` - server and friend "nicknames", set in discord server settings, not always by you.

``login`` is closest concept to IRC nicknames, as it's globally-unique,
consistent, short, ascii-only, and can be used by setting
``name-preference-order = login`` option in [discord] section (not the default).

Official discord clients display other names first, which is why
``name-preference-order`` option defaults to ``nick display login`` value,
which uses discord/friend-specific nicknames first, if any, falling back to
free-form name that user set in account settings, and their login name otherwise.

Other things in fancy user-set nicknames that IRC doesn't allow also get replaced
with common unicode characters, spaces with "·" middle-dots for example, or <>
common irc-nick brackets with ◄► unicode arrows. Long Discord nicks are truncated.

There are no IRC notifications about users changing their discord-specific
display/nick-names at the moment, and they don't have to be unique,
which might make it hard to tell who-is-who, if they keep changing nicks for
whatever reason.

All this is configurable via ini file settings (or in #rdircd.control channel),
so if it gets too silly and maddening, set ``name-preference-order = login``
to use unique consistent IRC-friendly nicks for everyone instead.

IRC ``/who`` command or ``/topic info`` can help translating between these names,
for example ``/t info john1234`` can be used to print info for that name/login
in the channel buffer, which should include all users with partial match of that
name on that specific discord, while ``/who`` command searches all joined discords.

.. _not the case with Discord:
  https://support.discord.com/hc/en-us/articles/12620128861463-New-Usernames-Display-Names

Local Name Aliases
``````````````````

(more like "renames" than "aliases", as old names don't continue to work for these)

Can be defined in the config file to replace hash-based discord prefixes or server
channel names with something more readable/memorable or meaningful to you::

  [renames]
  guild.jvpp = game-x
  guild.sn3y = log-bot
  guild.sn3y.chan-fmt = logs/{name}.log
  chan.some-long-and-weird-name = weird
  chan.@710035588048224269 = general-subs

This should:

- Turn e.g. #jvpp.info into #game-x.info - lettersoup guild-id to more
  meaningful prefix. This will apply to all channels in that discord -
  "guild" renames.

- Change format for channel names of "sn3y" discord from something like
  #sn3y.debug to #logs/debug.log - changing of channel name format.

  Format template uses `python str.format syntax`_ with "name" (channel name)
  and "prefix" (guild prefix - will be "log-bot" in this example) values.
  Default format is ``{prefix}.{name}``.

  This format option does not affect monitor/leftover channel name(s)
  (e.g. #rdircd.monitor.log-bot or #rdircd.leftover.game-x) -
  see "chan-monitor-guild" and "chan-leftover-guild" options under
  [irc] section for changing that.

- Rename that long channel to have a shorter name (retaining guild prefix) -
  "chan" renames.

  Note that this affects all guilds where such channel name exists, and source name
  should be in irc format, same as in /list, and is rfc1459-casemapped (same as on irc).

- Rename channel with id=710035588048224269 to "memes" (retaining guild prefix) -
  "chan" renames using \@channel-id spec.

  That long discord channel identifier (also called "snowflake") can be found by
  typing ``/t info`` topic-command in corresponding irc channel, and can be used
  to refer to that specific channel, i.e. renaming this one #general on this one
  discord server instead of renaming all #general channels everywhere.

  This is especially useful when two channels have same exact name within same
  discord, and normally will be assigned ``.<id-hash>`` non-descriptive suffixes.

Currently only listed types of renaming are implemented, for discord prefixes
and channels, but there are also options under [irc] section to set names for
system/monitor/leftover and private-chat channels - "chan-sys", "chan-private",
"chan-monitor" and such (see `"./rdircd --conf-dump-defaults" output`_).

Set ``chan-monitor-guild = {prefix}`` there for example, to have #game-x channel be
catch-all for all messages in that discord, without default long #rdircd.monitor.\* prefix.

.. _python str.format syntax: https://docs.python.org/3/library/string.html#format-string-syntax

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

See also `Auto-joining channels`_ section below for an easy way to pop-up
new private chats in the IRC client via invites.

Discord channel threads / forums
````````````````````````````````

"Threads" is a Discord feature, allowing non-admin users to create transient
ad-hoc sub-channels anytime for specific topic, which are auto-removed
("archived") after a relatively-short inactivity timeout (like a day).

Discord "forum" channels are basically channels, where people can only create
and talk in theads, with listing of those replacing default channel chatter.

All non-archived threads should be shown in rdircd channel list as a regular IRC
channels, with names like #gg.general.=vot5.lets·discuss·stuff, extending parent
chan name with thread id tag ("=vot5" in this example) and a possibly-truncated
thread name (see "thread-chan-name-len" config option).

There are several options for how to see and interact with threads from the
parent channel (mostly in [discord] section, `see --conf-dump-defaults output`_)::

  [irc]
  thread-chan-name-len = 30

  [discord]
  thread-id-prefix = =
  thread-msgs-in-parent-chan = yes
  thread-msgs-in-parent-chan-monitor = no
  thread-msgs-in-parent-chan-full-prefix = no
  thread-redirect-prefixed-responses-from-parent-chan = yes
  ...

But even with all these disabled, a simple notice should be sent to the channel
when threads are started, so that one won't miss them entirely.

There's no support for creating new threads from IRC, unarchiving old ones or
otherwise managing these, and joining thread channel in IRC doesn't actually
"join thread" in Discord UI (pining it under channel name), but posting anything
there should do that automatically.

.. _see --conf-dump-defaults output: rdircd.defaults.ini

Auto-joining channels
`````````````````````

"chan-auto-join-re" setting in "[irc]" section allows to specify regexp to match
channel name (without # prefix) to auto-join when any messages appear in them.

For example, to auto-join any #me.\* channels (direct messages), following
regular expression value (`python "re" syntax`_) can be used::

  [irc]
  chan-auto-join-re = ^me\.

| Or to have irc client auto-join all channels, use ``chan-auto-join-re = .``
| Empty value for this option (default) will match nothing.

This can be used as an alternative to tracking new stuff via
#rdircd.monitor/leftover channels.

This regexp can be tweaked at runtime using "set" command in #rdircd.control
channel, same as any other values, to e.g. temporary enable/disable this feature
for specific discords or channels.

Discord user mentions
`````````````````````

These are ``@username`` tags on discord, designed to alert someone to direct-ish message.

With default config, when you see e.g. ``<Galaxy🌌·Brain> Hi!`` and want to
reply highlighting them, sending ``Hey @galaxy and welcome`` should probably work.
Can also use their full irc nick, to be sure.

How it works: if rdircd matches ``msg-mention-re`` regexp conf-option against
something in a message being sent (e.g. ``@galaxy`` @-mention above), that'd be
treated as a "mention", which is either uniquely-matched and translated into a
discord mention in the sent message, or returns an error notice (with nicks that
match that mention ambiguously, if any).

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

  msg-mention-re = ^(?P<nick>[^\s,;@+]+)(: )

And should translate e.g. ``mk-fg: some msg`` into ``@mk-fg some msg``
(with @-part being mention-tag). Trailing space is included in regexp there
to avoid matching URL links.

To ID specific discord user, "nick" group will be used in following ways:

- Case-insensitive match against all recent guild-related irc names
  (message authors, reactions, private channel users, etc).
  ``user-mention-cache-timeout`` config option controls "recent" timeout.

- Lookup unique name completion by prefix, same as discord does in webui for
  auto-completion after @ is typed.

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

Quick edits/deletes for just-sent messages
``````````````````````````````````````````

Similar to `Discord user mentions`_ above, there's a special regexp-option that
matches commands to be interpreted as edit or removal of last message sent to
this channel.

Default regexps look something like this (check `--conf-dump-defaults`_ jic)::

  [discord]
  msg-edit-re = ^\s*s(?P<sep>[/|:])(?P<aaa>.*)(?P=sep)(?P<bbb>.*)(?P=sep)\s*$
  msg-del-re = ^\s*//del\s*$

They match sed/perl/irc-like follow-up amendment lines like ``s/spam/ham/``, and
``//del`` line, which will never be sent to discord, only used as internal commands.

(``s|/some/path|/other/path|`` and
``s:cat /dev/input/mouse0 | hexdump:hexdump </dev/input/mouse0:``
syntaxes are also allowed by default edit-regexp, just like with sed_, for
easier handling of common stuff like paths, which can have these chars in them)

Both commands matched by these operate on last message sent by rdircd to the
same discord channel, with ``//del`` simply removing that last message, and edit
running `python re.sub()`_ (`PCRE-like`_) regexp-replacement function on it.

"msg-edit-re" regexp option value matching sed-like command must have named
"aaa" and "bbb" groups in it, which will be used as pattern and replacement
args to re.sub(), respectively.

If edit doesn't seem to alter last-sent message in any way, it gets discarded,
and also generates IRC notice response, to signal that replacement didn't work.

Successful edit/deletion should also be signaled as usual by discord,
with "[edit]" or such prefix (configurable under "[irc]" section).

Any older-than-last messages can be edited through Discord WebUI - this client
only tracks last one for easy quick follow-up oops-fixes, nothing more than that.

.. _--conf-dump-defaults: rdircd.defaults.ini
.. _sed: https://en.wikipedia.org/wiki/Sed
.. _python re.sub(): https://docs.python.org/3/library/re.html#re.sub
.. _PCRE-like: https://en.wikipedia.org/wiki/Perl_Compatible_Regular_Expressions

@silent messages and other such flags
`````````````````````````````````````

Somewhat similar to quick edits/deletes above, "msg-flag-silent-re" option is
there to match/remove "@silent" prefix in messages (by default), which disables
sending discord push notifications for it, same as with the official client.

That and similar message flags on incoming messages are not represented
in any way, as they don't seem to be relevant for an irc client anyway.

Custom replacements/blocks in outgoing messages
```````````````````````````````````````````````

Config can have a [send-replacements] section to block or regexp-replace
parts of messages sent (by you) from IRC on per-discord basis.

This can be used to add discord-specific tags, unicode shorthands, emojis,
stickers, block/replace specific links or maybe even words/language before
proxying msg to discord.

Here's how it can look in the ini file(s)::

  [send-replacements]

  *.unicode-smiley = (^| ):\)( |$) -> \1😀\2
  *.twitter-to-nitter = ^(https?://)((mobile|www)\.)?twitter\.com(/.*)?$ -> \1nitter.ir\4

  guildx.never-mention-rust! = (?i)\brust\b -> <block!>
  guildx.localize-color-word = \bcolor(ed|i\S+)\b -> colour\1

Where each key has the form of ``discord-prefix> "." comment``, with a special
``*`` prefix to apply rule to all discords, while values are
``regexp " -> " <replacement_or_action`` with one special ``<block!>``
action-value to block sending msg with error-notice on regexp match.
"comment" part of the key can be any arbitrary unique string.

So when sending e.g. ``test :)`` msg on IRC, discord will get ``test 😀``.

Same as with other regex-using options, regexps have python "re" module syntax,
applied via `re.sub()`_ function, using raw strings from config value as-is,
without any special escapes or interpretations.

Replacements are applied in the same order as specified, but with ``*`` keys
preceding per-discord ones, and before processing to add discord tags, so anything
like @username that can normally be typed in messages can be used there too.

#rdircd.control channel has "repl" command to edit these rules on-the-fly.

.. _re.sub(): https://docs.python.org/3/library/re.html#re.sub

Custom filtering for all received messages
``````````````````````````````````````````

If you join #rdircd.monitor channel, see - for example - a message like this::

  <helper-bot> #pub.welcomes :: Welcome!

...and think "don't want to see messages like that again!" - config files'
"[recv-regexp-filters]" section or corresponding "rx" command in #rdircd.control
channel can help.

Depending on what "messages like that" means, here are some ways to filter those out::

  [recv-regexp-filters]
  discard msgs from this bot = ^<helper-bot>
  ignore all msgs in that channel of that discord = ^\S+ #pub\.welcomes ::
  drop all msgs from "pub" discord = ^\S+ #pub\.
  no messages from #welcomes channels of any discord pls = ^\S+ #\w+\.welcomes ::
  never see "Welcome!" message-text again!!! = ^\S+ #\S+ :: Welcome!$
  some combination of the above = (?i)^<helper-bot> #\w+\.welcomes ::
  ...

(tweak e.g. `last example on regex101.com`_ for more hands-on understanding)

Lines in that section have the usual ``<key> = <regexp>`` form, where <key>
part can be anything (e.g. comment to explain regexp, like in examples above),
and <regexp> value is a regular expression to match against the message in
``<user> #discord.channel-name :: message text`` format like that helper-bot
msg presented above, and same as can be seen in monitor-channels.

Any message received from discord will be matched against all regexps in order,
stopping and discarding the message everywhere on first (any) match.
So it might be a good idea to write as precise patterns as possible, to avoid
them matching anything else and dropping unrelated messages accidentally.

Same as with some other conf options, basic knowledge of regular expressions
might be needed to use such filters - `here's a link to nice tutorial on those`_
(though there are 100s of such tutorials on the web).

Particular regexps here use PCRE-like `python re syntax`_, with re.DOTALL
flag set (``.`` matches newlines in multiline messages).
I'd also recommend commonly adding ``(?i)`` case-insensitive-match flag,
as IRC nicks and channel names ignore character case and can be displayed
in misleading/inprecise ways in the client.

More random examples of recv-regexp-filters, incl. more advanced CNF weirdness::

  [recv-regexp-filters]
  disregard wordle thread there = ^\S+ #pub\.general\.=w8mk\.wordle ::
  ignore "wordle" threads everywhere = ^\S+ #\S+\.=\w{4}\.wordle ::
  activity-level bots are annoying = (?i) advanced to level \d+[ !]

  ;; Advanced stuff: connect multiple regexps via CNF logic (Conjunctive Normal Form)
  ;; If key starts with "∧ " (conjunction symbol), it's AND'ed with previous regexp
  ;; ¬ (negation) in that prefix inverts the logic, so e.g. "∧¬ ..." is "and not ..."
  ;; Disjunction (∨) is the default behavior and doesn't need the (implied) prefix
  ;; Any complex logical expression can be converted to such CNF form -
  ;;  - use calculators like https://www.dcode.fr/boolean-expressions-calculator

  Drop welcome msgs in welcome-chans = (?i)^\S+ #\w+\.\S*welcome\S* :: .*\bwelcome\b.*
  ∧ but only if they have an exclaimation mark in them somewhere = :: .*!
  ∧¬ and not from this specific "lut" discord-prefix = ^\S+ #lut\.

  Most channels here are not relevant = ^\S+ #myc\.
  ∧¬ except these ones = ^\S+ #myc\.(announcements|changelog|forum)[. ]
  ∨ but skip github CI logs there = ^<github> #myc\.

Pretty much anything can be matched with clever regexps, so CNF-logic stuff
like in last examples is seldom useful, but might still be simplier than
expressing arbitrary ordering or negation in regexps.

.. _last example on regex101.com: https://regex101.com/r/VMvyfS/2
.. _python re syntax: https://docs.python.org/3/howto/regex.html
.. _here's a link to nice tutorial on those: https://github.com/ziishaned/learn-regex

Lookup Discord IDs
``````````````````

Mostly useful for debugging - /who command can resolve specified ID
(e.g. channel_id from protocol logs) to a channel/user/guild info:

- ``/who #123456`` - find/describe channel with id=123456.
- ``/who %123456`` - server/guild id info.
- ``/who @123456`` - user id lookup.

All above ID values are unique across Discord service within their type.

- ``/who @John·Mastodon`` - user IRC nick or name/login lookup.

  Queries all joined discords for that name, and can return
  multiple results for same or similar non-unique names.
  Can be useful to check exact nick/display/login names
  corresponding to an IRC name, or other user info.

Results of all these commands should be dumped into a server buffer
(not into channels), regardless of where they were issued from.

Channel name disambiguation
```````````````````````````

Discord name translation is "mostly" deterministic due to one exception -
channels with same (casemapped) IRC name within same server/guild,
which discord allows for.

When there is a conflict, chan names are suffixed by ``.<id-hash>``
(see chan-dedup-\* config options), to allow using both channels through IRC.
Renaming conflicting channels on Discord will rename IRC chans to remove
no-longer-necessary suffixes as well. Such renames affect thread-channels too.

Note that when channels are renamed (including name conflicts),
IRC notice lines about it are always issued in affected channels,
and any relevant monitor/leftover channels, topic should be changed
to reflect that old-name channel is no longer useful, and posting msgs
there should emit immediate warnings about it.

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

Captcha-solving is required to login for some reason
````````````````````````````````````````````````````

Don't know why or when it happens, but was reported by some users in this and
other similar discord clients - see `issue-1`_ here and links in there.

Fix is same as with bitlbee-discord_ - login via browser, maybe from the same
IP Address, and put auth token extracted from this browser into configuration
ini file's [auth] section, e.g.::

  [auth]
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

Almost every message I see are reacts by people :(
``````````````````````````````````````````````````

There is `an ini file option`_ for this::

  [irc]
  ...
  ; disable-reactions: disables all "--- reacts" messages
  disable-reactions = no

Flip that to "yes" in config to disable all those, or alternatively they can be
blocked in a more fine-grained way in the IRC client.

There's a bunch of other similar tweaks that can be useful in there too.

.. _an ini file option: rdircd.defaults.ini

Debugging anything strange, unknown or unexpected
`````````````````````````````````````````````````

Most likely source of that should be missing handling for some new/uncommon
discord events, or maybe a bug in the code somewhere - either can be reported as
a github issue.

To get more information on the issue (so that report won't be unhelpful "don't work"),
following things can be monitored and/or enabled:

- Standard error stream (stderr) of the script when problem occurs and whether
  it crashes (unlikely).

  If rdircd is run as a systemd service, e.g. ``journalctl -au rdircd`` should
  normally capture its output, but there are other ways to enable logs listed just below.

  rdircd shouldn't normally ever crash, as it handles any errors within its own
  loop and just reconnects or whatever, but obviously bugs happen - there gotta
  be some python traceback printed to stderr on these.

- Find a way to reproduce the issue.

  When something weird happens, it's most useful to check whether it can be
  traced to some specific discord and event there (e.g. some new feature being used),
  or something specific you did at the time, and check whether same thing
  happens again on repeating that.

  That's very useful to know, as then problem can be reproduced with any kind of
  extra logging and debugging aids enabled until it's perfectly clear what's
  going on there, or maybe how to avoid it, if fixing is not an option atm.

- Join #rdircd.debug channel - any warnings/errors should be logged there.

  Send "help" (or "h") msg to it to see a bunch of extra controls over it.

  Sending "level debug" (or "d") there for example will enable verbose debug
  logging to that channel (can be disabled again via "level warning"/"w"),
  but it might be easier to use log files for that - see below.

- Enable debug and protocol logs to files.

  In any loaded rdircd ini file(s), add [debug] section with options like these::

    [debug]
    log-file = /var/log/rdircd/debug.log
    proto-log-shared = no
    proto-log-file = /var/log/rdircd/proto.log

  ``/var/log/rdircd`` dir in this example should be created and accessible only
  to running rdircd and ideally nothing else, e.g. creating it as:
  ``install -m700 -o rdircd -d /var/log/rdircd``

  Such opts should enable those auto-rotating log files, which will have a lot
  of very information about everything happening with the daemon at any time.

  Both of these can also be enabled/controlled and/or queried at runtime from
  #rdircd.debug chan.

  ``proto-log-shared`` option (defaults to "yes") and be used to send
  discord/irc protocol logging to same log-file or #rdircd.debug channel,
  but it might be easier to have two separate logs, as in example above.

  Log file size and rotation count can be set via ``log-file-size``,
  ``log-file-count``, ``proto-log-file-size``, ``proto-log-file-count``
  options - run ``rdircd --conf-dump-defaults`` to see all those and their
  default values (`rdircd.defaults.ini`_ has some recent-ish copy too).

  When running with protocol logs repeatedly or over long time,
  ``proto-log-filter-ws`` option can be handy to filter-out spammy
  uninteresting events there, like GUILD_MEMBER_LIST_UPDATE.

  Note that these files will contain all sorts of sensitive information - from
  auth data to all chats and contacts - so should probably not be posted or
  shared freely on the internet in-full or as-is, but can definitely help to
  identify/fix any problems.

- Running ``/version`` IRC-command should at least print something like
  ``host 351 mk-fg 22.05.1 rdircd rdircd discord-to-irc bridge`` on the first line,
  which is definitely useful to report, if it's not the latest one in this git repo.

Generally if an issue is easy to reproduce (e.g. "I send message X anywhere and
get this error"), it can be reported without digging much deeper for more info,
as presumably anyone debugging it should be able to do that as well, but maybe
info above can still be helpful to identify any of the more non-obvious problems,
or maybe give an idea where to look at for fixing or working around these.


Random tips and tricks
----------------------

Some cool configurations mentioned in #rdircd on IRC and such.

Simplier DM and monitor channel names
`````````````````````````````````````

Normally rdircd uses these long strange "#rdircd.monitor" channel name
templates, as well as unnecessary "#me.chat."  prefixes, instead of this::

  #DMs
  #@some-friend
  #@some-friend+other-friend+more-ppl
  #rdircd
  #rdircd.control
  #rdircd.debug
  #minecraft
  #minecraft.general
  #minecraft.modding

Use these lines in any loaded ini config file to make it work like that::

  [irc]
  chan-monitor = rdircd
  chan-monitor-guild = {prefix}
  chan-private = {names}

  [renames]
  guild.me = DMs
  guild.me.chan-fmt = @{name}

What these options do, in the same order: rename "#rdircd.monitor" to "#rdircd",
set names for all discord-specific monitor channels to just "{prefix}"
(e.g. "#dm" or "#minecraft"), set private-chat channels to use people's name(s)
without "chat." prefix, rename default "me" guild (private chats) to "DMs",
use simplier @ + name format for any channels there.

Defaults are that way to try to be more explicit and descriptive,
but once you know what all these channels are for, can easily rename
them to something shorter/nicer and more convenient for yourself.

Change message edit/embed/attachment prefixes to shorter emojis
```````````````````````````````````````````````````````````````

When message is edited, you normally get something like ``[edit] new msg text``,
but it can be ``✍️ new msg text`` or ``📝 new msg text`` instead::

  [irc]
  prefix-edit = 📝 \
  prefix-embed = 📎.{} \
  prefix-attachment = 🖼️ \
  prefix-uis = ⚙️ \
  prefix-call = 📞 \

Note the "space and backslash" at the end in these options, which is to preserve
trailing spaces in values, from both text editors that strip those and configuration
file parser (which ignores any leading/trailing spaces, unless punctuated by backslash).
``prefix-embed`` option value needs ``{}`` placeholder for where to put its short id/tag.

Alternatively, set-command like ``set irc-prefix-edit '✍️ '`` can be used in #rdircd.control
to configure and tweak this stuff on-the-fly (or ``-s/--save`` into config too).


Links
-----

Other third-party Discord clients that I'm aware of atm (2023-05-23),
in no particular order.

Other lists of clients, maybe better-maintained than this one:

- `Discord-Client-Encyclopedia-Management/Discord3rdparties`_

IRC-translation clients (like this one):

- bitlbee_ + bitlbee-discord_ - similar IRC interface
- bitlbee_ + libpurple (from Pidgin_) + purple-discord_ - diff implementation from above

Graphical UI (GUI) clients:

- Pidgin_ + purple-discord_ - popular cross-platform IM client
- gtkcord4_ - Go/GTK4 client, which also works on linuxy phones
- Ripcord_ - cross-platform proprietary shareware client, also supports slack

Terminal UI (TUI, ncurses) clients:

- discordo_ - relatively new but popular client written in Go.
- 6cord_ - Go client, seem to be deprecated atm in favor of gtkcord
- Cordless_ - fairly mature Go TUI client, abandoned after discord blocking dev's acc
- weechat-discord_ - Weechat terminal IRC client plugin to connect to Discord

Web UI (in-browser) clients/mods (often further extended by plugins):

- BetterDiscord_ and its BandagedBD_ fork - alternative in-browser web interface/client
- Powercord_ - privacy and client extension oriented mod/framework
- Replugged_ - "big and slow"
- Vencord_ - "cutest Discord client mod"
- Shelter_ - stability and maintainability focus
- ... many-many more of these around, though note that browser client mods are explicitly against ToS, not just guidelines.

Command-line clients:

- Harmony_ - tool for discord account manipulation - e.g. create, change settings, accept invites, etc

Not an exhaustive list by any means, they seem to be popping-up and closing down
pretty fast, and I don't really keep track of those in any meaningful way.

If you know of other maintained clients (or better yet a list of those), maybe
drop a link into irc channel, repo issues or wherever - would be nice to add it
here, for anyone looking for alternatives.

.. _Discord-Client-Encyclopedia-Management/Discord3rdparties:
  https://github.com/Discord-Client-Encyclopedia-Management/Discord3rdparties
.. _bitlbee: https://www.bitlbee.org/
.. _Pidgin: https://pidgin.im/
.. _purple-discord: https://github.com/EionRobb/purple-discord
.. _gtkcord4: https://github.com/diamondburned/gtkcord4
.. _Ripcord: https://cancel.fm/ripcord/
.. _BandagedBD: https://github.com/rauenzi/BetterDiscordApp
.. _BetterDiscord: https://github.com/BetterDiscord/BetterDiscord
.. _Powercord: https://powercord.dev/
.. _Replugged: https://replugged.dev/
.. _Vencord: https://vencord.dev/
.. _Shelter: https://github.com/uwu/shelter
.. _discordo: https://github.com/ayntgl/discordo
.. _6cord: https://gitlab.com/diamondburned/6cord/
.. _Cordless: https://github.com/Bios-Marcel/cordless
.. _weechat-discord: https://github.com/terminal-discord/weechat-discord
.. _Harmony: https://github.com/nickolas360/harmony


More info on third-party client blocking
----------------------------------------

As mentioned in the "WARNING" section above, `Bot vs User Accounts`_
section in API docs seem to prohibit people using third-party clients,
same as `Discord Community Guidelines`_.
Also maybe against their `Discord Developer Terms of Service`_,
but dunno if those apply if you're just using the alt-client.

.. _Discord Community Guidelines: https://discord.com/guidelines
.. _Discord Developer Terms of Service:
  https://discord.com/developers/docs/policies-and-agreements/developer-terms-of-service

I did ask discord staff for clarification on the matter,
and got this response around Nov 2020:

    Is third-party discord client that uses same API as webapp, that does not
    have any kind of meaningful automation beyond what official discord app has,
    will be considered a "self-bot" or "user-bot"?

    I.e. are absolutely all third-party clients not using Bot API in violation
    of discord ToS, period?

    Or does that "self-bot" or "user-bot" language applies only to a specific
    sub-class of clients that are intended to automate client/user behavior,
    beyond just allowing a person to connect and chat on discord normally?

  Discord does not allow any form of third party client, and using a client like
  this can result in your account being disabled.  Our API documentation
  explicitly states that a bot account is required to use our API: "Automating
  normal user accounts (generally called "self-bots") outside of the OAuth2/bot
  API is forbidden, and can result in an account termination if found."

Another thing you might want to keep in mind, is that apparently it's also
considered to be responsibility of discord admins to enforce its Terms of
Service, or - presumably - be at risk of whole guild/community being shut down.

Got clarification on this issue in the same email (Nov 2020):

    Are discord server admins under obligation to not just follow discord Terms
    of Service themselves (obviously), but also enforce them within the server
    to the best of their knowledge?

    I.e. if discord server admin knows that some user is in violation of the
    ToS, are they considered to be under obligation to either report them to
    discord staff or take action to remove (ban) them from the server?

    Should failing to do so (i.e. not taking action on known ToS violation)
    result in discord server (and maybe admins' account) termination or some
    similar punitive action, according to current discord ToS or internal policies?

  Server owners and admin are responsible for moderating their servers in
  accordance with our Terms of Service and Community Guidelines.
  If content that violates our Terms or Guidelines is posted in your server,
  it is your responsibility to moderate it appropriately.

So unless something changes or I misread discord staff position,
using this client can get your discord account terminated,
and discord admins seem to have responsibility to ban/report its usage,
if they are aware of it.

Few other datapoints and anecdotes on the subject:

- Don't think Discord's "Terms of Service" document explicitly covers
  third-party client usage, but "Discord Community Guidelines" kinda does,
  if you consider this client to be "self-bot" or "user-bot" at least.

  Only thing that matters in practice is likely the actual staff and specific
  server admins' position and actions on this matter, as of course it's a
  private platform/communities and everything is up to their discretion.

- Unrelated to this client, one person received following warning (2020-01-30)
  after being reported (by another user) for mentioning that they're using
  BetterDiscord_ (which is/was mostly just a custom css theme at the time, afaik):

  .. image:: discord-tos-violation-warning.jpg

- In September 2021 there was a bunch of issues with people using different
  third-party clients being asked to reset their passwords daily due to
  "suspicious activity", raised here in `issue-18`_ (check out other links there too),
  which seem to have gone away within a week.

  At least one person in that issue thread also reported being asked for phone
  account verification for roughly same reason about a week after that, so maybe
  "suspicious activity" triggering for 3p clients haven't really gone away.

- Cordless_ client developer's acc apparently got blocked for ToS violation when
  initiating private chats. This client doesn't have such functionality, but
  maybe one should be more careful with private chats anyway, as that seem to be
  a major spam vector, so is more likely to be heavily-monitored, I think.

- In the #rdircd IRC channel, a person mentioned that their discord account got
  some anti-spam mechanism enabled on it, disallowing to log-in without
  providing a phone number and SMS challenge (and services like Google Voice
  don't work there), immediately after they've initiated private chat with
  someone in Ripcord_ client.

  "I contacted support at the time and they just responded that they can't
  undo the phone number requirement once it has been engaged"

  It also seems like Ripcord currently might be trying to mimic official client
  way more closely than rdircd script here does (where latter even sends
  "client"/"User-Agent" fields as "rdircd" and appears that way under Devices in
  User Settings webui), and such similarity might look like Terms of Service
  violation to Discord (modifying official client), instead of Community
  Guidelines violation (third-party client), but obviously it's just a guess
  on my part as to whether it matters.

There are also `some HN comments clarifying Discord staff position in a thread here`_,
though none of the above should probably be taken as definitive,
since third-party and even support staff's responses can be wrong/misleading or outdated,
and such treatment can likely change anytime and in any direction,
without explicit indication.

.. _issue-18: https://github.com/mk-fg/reliable-discord-client-irc-daemon/issues/18
.. _some HN comments clarifying Discord staff position in a thread here:
  https://news.ycombinator.com/item?id=25214777


API and Implementation Notes
----------------------------

Note: only using this API here, only going by public info, can be wrong,
and would appreciate any updates/suggestions/corrections via open issues.

Last updated: 2023-05-23

- Discord API docs don't seem to cover "full-featured client" use-case,
  because such use of its API is explicitly not supported, against their
  rules/guidelines, and presumably has repercussions if discovered.

  See WARNING section above for more details.

- Discord API protocol changes between version, which are documented on
  `Change Log page of the API docs`_.

  Code has API number hardcoded as DiscordSession.api_ver, which has to be
  bumped there manually after updating it to handle new features as necessary.

- Auth uses undocumented /api/auth/login endpoint for getting "token" value for
  email/password, which is not OAuth2 token and is usable for all other endpoints
  (e.g. POST URLs, Gateway, etc) without any prefix in HTTP Authorization header.

  Found it being used in other clients, and dunno if there's any other way to
  authorize non-bot on e.g. Gateway websocket - only documented auth is OAuth2,
  and it doesn't seem to allow that.

  Being apparently undocumented and available since the beginning,
  guess it might be heavily deprecated by now and go away at any point in the future.

- There are some unofficial docs for officially-undocumented APIs and quirks:

  - https://luna.gitlab.io/discord-unofficial-docs/ (+ litecord_ api-testing server)
  - https://github.com/Merubokkusu/Discord-S.C.U.M/tree/master/docs

- Sent message delivery confirmation is done by matching unique "nonce" value in
  MESSAGE_CREATE event from gateway websocket with one sent out to REST API.

  All messages are sent out in strict sequence (via one queue), with synchronous
  waiting on confirmation, aborting whole queue if first one fails to be delivered,
  with notices for each failed/discarded msg.

  This is done to ensure that all messages either arrive in the same strict
  order they've been sent or not posted at all.

- Fetching list of users for discord channel or even guild does not seem to be
  well-supported or intended by the API design.

  There are multiple opcodes that allow doing that in a limited way, none of
  which work well for large discords (e.g. 10k+ users).

  request_guild_members (8) doesn't return any results, request_sync (12)
  doesn't work, request_sync_chan (14) can be used to request small slice of the
  list, but only one at a time (disconnects on concurrent requests).

  Latter is intended to only keep part of userlist that is visible synced in the client,
  doesn't support proper paging through whole thing,
  and only gets updates for last-requested part with indexes in it -
  basically "I'm in this guild/channel, what should I see?" request from the client.

- Some events on gateway websocket are undocumented, maybe due to lag of docs
  behind implementation, or due to them not being deemed that useful to bots, idk.

- Discord allows channels (and probably users) to have exactly same name, which is not
  a big deal for users (due to one-way translation), but have to be disambiguated for channels.

- Gateway websocket `can use zlib compression`_, which makes inspecting protocol in
  browser devtools a bit inconvenient. `gw-ws-har-decode.py <gw-ws-har-decode.py>`_
  helper script in this repo can be used to decompress/decode websocket messages saved
  from chromium-engine browser devtools (pass -h/--help option for info on how to do it).

- Adding support for initiating private chats might be a bad idea, as Cordless_
  dev apparently got banned for that, as these seem to be main spam vector,
  so more monitoring and anomaly detection is likely done there, leading to
  higher risk for users.

.. _Change Log page of the API docs: https://discord.com/developers/docs/change-log
.. _litecord: https://gitlab.com/litecord/litecord
.. _can use zlib compression: https://discord.com/developers/docs/topics/gateway#encoding-and-compression
