# Reliable Discord-client IRC Daemon (rdircd)

Table of Contents

- [Description](#hdr-description)
- [WARNING]
- [Features](#hdr-features)
- [Limitations](#hdr-limitations)
- [Usage](#hdr-usage)

    - [Requirements](#hdr-requirements)
    - [Installation](#hdr-installation)
    - [Setup and actual usage](#hdr-setup_and_actual_usage)

- [Misc Feature Info](#hdr-misc_feature_info)

    - [Multiple Config Files](#hdr-multiple_config_files)
    - [Private Chats](#hdr-private_chats)
    - [Channel Commands](#hdr-channel_commands)
    - [#rdircd.monitor and #rdircd.leftover channels]
    - [People's names on discord]
    - [Local Name Aliases]
    - [Private messages and friends](#hdr-private_messages_and_friends)
    - [Discord channel threads / forums](#hdr-discord_channel_threads___forums)
    - [Auto-joining channels]
    - [Discord user mentions](#hdr-discord_user_mentions)
    - [Quick edits/deletes for just-sent messages]
    - [@silent messages and other such flags]
    - [Custom replacements/blocks in outgoing messages]
    - [Custom filtering for all received messages]
    - [Lookup Discord IDs]
    - [Channel name disambiguation]
    - [OSC 8 hyperlinks for terminal IRC clients]
    - [Voice chat activity notifications]
    - [Highlight on incoming private messages]
    - [Message ACKs, typing notifications and other events from IRC]
    - [WARNING :: Session/auth rejected unexpectedly - disabling connection]
    - [Captcha-solving is required to login for some reason]
    - [Debugging anything strange, unknown or unexpected]

- [Random tips and tricks](#hdr-random_tips_and_tricks)

    - [Simpler DM and monitor channel names]
    - [Change message edit/embed/attachment prefixes to shorter emojis]
    - [Cut down on various common noise]

- [Links]
- [More info on third-party client blocking]
- [API and Implementation Notes](#hdr-api_and_implementation_notes)

[WARNING]: #hdr-warning
[#rdircd.monitor and #rdircd.leftover channels]:
  #hdr-_rdircd.monitor_and_rdircd.leftover_channels
[People's names on discord]: #hdr-people_s_names_on_discord
[Local Name Aliases]: #hdr-local_name_aliases
[Auto-joining channels]: #hdr-auto-joining_channels
[Quick edits/deletes for just-sent messages]:
  #hdr-quick_edits_deletes_for_just-sent_messages
[@silent messages and other such flags]:
  #hdr-_silent_messages_and_other_such_flags
[Custom replacements/blocks in outgoing messages]:
  #hdr-custom_replacements_blocks_in_outgoing_m.NzCf
[Custom filtering for all received messages]:
  #hdr-custom_filtering_for_all_received_messages
[Lookup Discord IDs]: #hdr-lookup_discord_ids
[Channel name disambiguation]: #hdr-channel_name_disambiguation
[OSC 8 hyperlinks for terminal IRC clients]:
  #hdr-osc_8_hyperlinks_for_terminal_irc_clients
[Voice chat activity notifications]: #hdr-voice_chat_activity_notifications
[Highlight on incoming private messages]:
  #hdr-highlight_on_incoming_private_messages
[Message ACKs, typing notifications and other events from IRC]:
  #hdr-message_acks_typing_notifications_and_ot.9aX7
[WARNING :: Session/auth rejected unexpectedly - disabling connection]:
  #hdr-warning_session_auth_rejected_unexpected.ZboG
[Captcha-solving is required to login for some reason]:
  #hdr-captcha-solving_is_required_to_login_for.ls9P
[Debugging anything strange, unknown or unexpected]:
  #hdr-debugging_anything_strange_unknown_or_un.NQDm
[Change message edit/embed/attachment prefixes to shorter emojis]:
  #hdr-change_message_edit_embed_attachment_pre.xxnp
[Simpler DM and monitor channel names]:
  #hdr-simpler_dm_and_monitor_channel_names
[Cut down on various common noise]: #hdr-cut_down_on_various_common_noise
[Links]: #hdr-links
[More info on third-party client blocking]:
  #hdr-more_info_on_third-party_client_blocking



<a name=hdr-description></a>
## Description

rdircd is a daemon that allows using a personal [Discord] account through an [IRC] client.

It translates all private chats and public channels/threads on "discord servers"
into channels on an IRC server that it creates and that you can connect to using
regular IRC client, instead of a browser or electron app.

"reliable" is in the name because one of the initial goals was to make it confirm
message delivery and notify about any issues in that regard, which was somewhat
lacking in other similar clients at the time.

There's an IRC channel to talk about the thing - join [#rdircd at libera.chat].\
IRC URL: <ircs://irc.libera.chat/rdircd> (github refuses to make ircs:// links)

See also [Links] section below for rarely-updated list of other alternative clients.

Repository URLs:

- <https://github.com/mk-fg/reliable-discord-client-irc-daemon>
- <https://codeberg.org/mk-fg/reliable-discord-client-irc-daemon>
- <https://fraggod.net/code/git/reliable-discord-client-irc-daemon>

Last one has git-notes with todo list and such at the default ref for those.

[Discord]: http://discord.gg/
[IRC]: https://en.wikipedia.org/wiki/Internet_Relay_Chat
[#rdircd at libera.chat]: https://web.libera.chat/?channels=#rdircd


<a name=hdr-warning></a>
## WARNING

While I wouldn't call this app a "bot" or "automating standard user accounts" -
intent here is not to post any automated messages or scrape anything - pretty sure
Discord staff considers all third-party clients to be "bots", and requires them to
use special second-class API (see [Bot vs User Accounts] section in API docs),
where every account has to be separately approved by admins on every connected
discord server/guild, making it effectively unusable for a random non-admin user.

This app does not present itself as a "bot" and does not use bot-specific endpoints,
so using it can result in account termination if discovered.

See also [More info on third-party client blocking] section below.

You have been warned! :)

[Bot vs User Accounts]:
  https://discord.com/developers/docs/topics/oauth2#bot-vs-user-accounts


<a name=hdr-features></a>
## Features

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
  more than e.g. [bitlbee-discord], but better than those leaky browser tabs.

- Easy to tweak and debug without rebuilds, gdb, rust and such.

[bitlbee-discord]: https://github.com/sm00th/bitlbee-discord


<a name=hdr-limitations></a>
## Limitations

- Only user mentions sent from IRC are translated into discord tags
  (if enabled and with some quirks, see below) - not channels, roles, stickers,
  components or emojis.

- No support for sending attachments or embeds of any kind - use WebUI for that, not IRC.

  Discord automatically annotates links though, so posting media is as simple as that.

- No discord-specific actions beyond all kinds of reading and sending messages
  to existing channels are supported - i.e. no creating accounts or channels on discord,
  managing roles, invites, bans, timeouts, etc - use WebUI, [Harmony] or proper discord bots.

- Creating new private chats and channel/forum threads is not supported.

    For private chats, it might be even dangerous to support - see
    [More info on third-party client blocking] section below for details.

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

- [Slash commands] (for bots) are not supported in any special way,
  but you can probably still send them, if IRC client will pass these through.

- Not the most user-friendly thing, though probably same as IRC itself.

- I only run it on Linux, so it's unlikely to "just work" on OSX/Windows, but idk.

- Custom ad-hoc implementation of both discord and irc, not benefitting from any
  kind of exposure and testing on pypi and such wrt compatibility, bugs and corner-cases.

- Seem to be against Discord guidelines to use it - see WARNING section above for more details.

[Harmony]: https://github.com/nickolas360/harmony
[Slash commands]: https://discord.com/developers/docs/interactions/slash-commands


<a name=hdr-usage></a>
## Usage

<a name=hdr-requirements></a>
### Requirements

* [Python 3.8+](http://python.org/)
* [aiohttp](https://aiohttp.readthedocs.io/en/stable/)


<a name=hdr-installation></a>
### Installation

Simplest way might be to use package for/from your linux distribution, if it is available.

Currently known distro packages (as of 2020-05-17):

- Arch Linux (AUR): <https://aur.archlinux.org/packages/rdircd-git/>
- Termux (Android linux env): [termux/termux-packages/packages/rdircd]

There's also a [Dockerfile] and [docker-compose.yml] for running this
in a docker/podman or some other OCI-compatible containerized environment.\
(see also [README.docker-permissions.md] doc for info on common access issues with those)

Should be easy to install one script and its few dependencies manually as well,
as described in the rest of this section below.

On debian/ubuntu, installing dependencies can be done with this one command:

    # apt install --no-install-recommends python3-minimal python3-aiohttp

Other linux distros likely have similar packages as well, and I'd recommend
trying to use these as a first option, so that they get updates and to avoid
extra local maintenance burden, and only fallback to installing module(s) via
"pip" if that fails.

On any arbitrary distro with python (python3) installed, using pip/venv to
install aiohttp module (and its deps) to unprivileged "rdircd" user's home dir
might work (which is also used to run rdircd in the next example below),
but ignore this if you've already installed it via OS package manager or such:

```
root # useradd -m rdircd
root # su - rdircd

## Option 1: use venv to install dependencies into "_venv" dir

rdircd % python3 -m venv _venv
rdircd % ./_venv/bin/pip install aiohttp

## Option 2: install pip (if missing) and use it directly

rdircd % python3 -m ensurepip --user
rdircd % python3 -m pip install --user aiohttp
```

If you have/use [pipx] (e.g. from distro repos), it can be used to run python
apps like this one and auto-maintain dependencies - just "pipx run" the main
script: `pipx run rdircd --help` - without needing to touch venv or pip at all
(pipx will do it "under the hood").

After requirements above are installed, script itself can be fetched
from this repository and run like this:

```
## Ignore "useradd" if you've already created a user when running "pip" above
root # useradd -m rdircd
root # su - rdircd

## If using "venv" install example above - load its env vars
# Or alternatively run script via "./_venv/bin/python rdircd ..." command line
rdircd % source ./_venv/bin/activate

rdircd % curl -o rdircd https://raw.githubusercontent.com/mk-fg/reliable-discord-client-irc-daemon/master/rdircd
rdircd % chmod +x rdircd

## Use "pipx run rdircd ..." here and below, if using pipx instead of pip/venv/distro-pkgs
rdircd % ./rdircd --help
...to test if it runs...

rdircd % ./rdircd --conf-dump-defaults
...for a full list of all supported options with some comments...
...alternatively, to create rdircd.ini template: ./rdircd -c rdircd.ini --conf-init

rdircd % nano rdircd.ini
...see below for configuration file info/example...

rdircd % ./rdircd --debug -c rdircd.ini
...drop --debug and use init system for a regular daemon...
```

For setting up daemon/script to run on OS boot, [rdircd.service] systemd unit file
can be used in most Linux environments (edit ExecStart= options and paths there),
or otherwise probably via init.d script, or maybe in "screen" session as a
last resort ad-hoc option.
Make sure it runs as e.g. "rdircd" user created in snippet above, not as root.

To update the script later, if needed, replace it with a latest version,
e.g. via re-downloading with a curl command above, git-pull on the repo clone,
`docker-compose up --build`, updating os package, or in some other way,
usually related to how it got installed in the first place.

[termux/termux-packages/packages/rdircd]:
  https://github.com/termux/termux-packages/tree/master/packages/rdircd
[Dockerfile]: Dockerfile
[docker-compose.yml]: docker-compose.yml
[README.docker-permissions.md]: README.docker-permissions.md
[pipx]: https://pypa.github.io/pipx/
[rdircd.service]: rdircd.service


<a name=hdr-setup_and_actual_usage></a>
### Setup and actual usage

Create configuration file with discord and ircd auth credentials in ~/.rdircd.ini
(see all `--conf...` opts wrt these):

``` ini
[irc]
password = hunter2

[auth]
email = discord-reg@email.com
password = discord-password
```

Note: IRC password can be omitted, but make sure to firewall that port from
everything in the system then (or maybe do it anyway).

If you set password though, maybe do not use IRC `password=` option like above,
and use `password-hash=` and `-H/--conf-pw-scrypt` to generate it instead.
Either way, make sure to use that password when configuring connection to this
server in the IRC client as well.

Start rdircd daemon: `./rdircd --debug`

Connect IRC client to "localhost:6667" - default listen/bind host and port.

(see `./rdircd --conf-dump-defaults` or corresponding CLI `-i/--irc-bind` /
`-s/--irc-tls-pem-file` options for binding on different host/port and TLS
socket wrapping, for non-localhost connections)

Run `/list` to see channels for all joined discord servers/guilds:

    Channel           Users Topic
    -------           ----- -----
    #rdircd.control       1  rdircd: control channel, type "help" for more info
    #rdircd.debug         1  rdircd: debug logging channel, read-only
    #rdircd.monitor       1  rdircd: read-only catch-all channel with messages from everywhere
    #rdircd.leftover      1  rdircd: read-only channel for any discord messages in channels ...
    #rdircd.voice         1  rdircd: read-only voice-chat notifications from all discords/channels
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
- #rdircd.voice is also there to monitor only voice channel notifications from everywhere.
- Public IRC channel users are transient and only listed/counted if they sent
  something to a channel, as discord has no concept of "joining" for publics.
- Everything in that /list and everything used to talk through this app are IRC
  channels (with #, that you /join), it doesn't use /q or /msg pretty much anywhere.
- Channels always list at least 1 user, to avoid clients hiding ones with 0.

`/j #axsd.offtopic` (/join) as you'd do with regular IRC to start shitposting there.
Channels joins/parts in IRC side do not affect discord in any way.

Run `/topic` (often works as `/t`) irc-command to show more info on
channel-specific commands, e.g. `/t log` to fetch and replay backlog starting
from last event before last rdircd shutdown, `/t log list` to list all
activity timestamps that rdircd tracks, or `/t log 2h` to fetch/dump channel
log for/from specific time(stamp/span) (iso8601 or a simple relative format).

Daemon control/config commands are available in #rdircd.control channel,
#rdircd.debug chan can be used to tweak various logging and inspect daemon state
and protocols more closely, send "help" there to list available commands.

For broad outline of various supported configuration settings,
see [rdircd.defaults.ini] file (output of `./rdircd --conf-dump-defaults`),
and more on particular uses of those below.

[rdircd.defaults.ini]: rdircd.defaults.ini


<a name=hdr-misc_feature_info></a>
## Misc Feature Info

Notes on various optional and less obvious features are collected here.\
See "Usage" section for a more general information.

<a name=hdr-multiple_config_files></a>
### Multiple Config Files

Multiple ini files can be specified with `-c` option, overriding each other in sequence.

Last one will be updated wrt \[state\], token= and similar runtime stuff,
as well as any values set via #rdircd.control channel commands,
so it can be useful to specify persistent config with auth and options,
and separate (initially empty) one for such dynamic state.

E.g. `./rdircd -c config.ini -c state.ini` will do that.\
`--conf-dump` can be added to print resulting ini assembled from all these.\
`--conf-dump-defaults` flag can be used to list all options and their defaults.

Frequent state timestamp updates are done in-place (small fixed-length values),
but checking ctime before writes, so should be safe to edit any of these files
manually anytime anyway.

Sending SIGHUP to the script or "reload" command in control-channel should
load and apply values from all config files in the same order.
Note that such operation won't reset any values missing in files to their
defaults, only apply stuff explicitly set there on top of the current config.

<a name=hdr-private_chats></a>
### Private Chats

ALL chats in rdircd (and discord) are **a channel**.\
IRC's /q, /query and /msg **cannot be used** in an IRC-typical way.\
To talk in any private chat, **join a channel** like #me.chat.\<username\>,
which behaves like any other discord/rdircd channels.

There is currently no way to create new private chats from rdircd,
use other clients or WebUI for that (or ask someone to contact you first),
but once private chat channel is created, it can be used in rdircd as well.

See also [Auto-joining channels] and/or [/join e.g. #rdircd.leftover.me channel]
to monitor private messages reliably, if needed.

[/join e.g. #rdircd.leftover.me channel]:
  #hdr-_rdircd.monitor_and_rdircd.leftover_channels

<a name=hdr-channel_commands></a>
### Channel Commands

In all IRC channels representing a discord channel - send `/topic`
(or `/t` - shorthand for it often supported in IRC clients) - which
should print up-to-date info on all channel-specific commands, like those:

- `/t info` - show some internal guild/channel information, like IDs and such for renames.

    Should print exact channel name on discord (without any [local renames] or
    discord-to-irc translation that rdircd does), its topic, type, etc, among
    other things.

- `/t info {user-name...}` - query info on user name (or part of it) in this discord.

    For example, `/t info joe137` will lookup `joe137` user on a discord server that
    channel belongs to, printing info about them, like their [various discord names].

- `/t log [state]` - replay history since "state" point (last rdircd stop by default).

    `/t log` (same as `/t log 1`) can be used e.g. after rdircd restart
    to query discord for any messages that might've been posted after it was stopped,
    and before it was started back again (plus any others since then).\
    Or `/t log 0` to check history since last msg that rdircd has seen,
    for cases when discord/network is flakey and something might've been lost that way.\
    (where these `1` and `0` numbers refer to saved timestamps from `/t log list`
    output, stored/updated under `[state]` in the ini file)

    It can also be used with an absolute or relative time, e.g. `/t log 15m`
    to request/replay channel history within last 15 minutes, or `/t log
    2019-01-08 12:30` to replay history since that specific rdircd-local time
    (unless timezone is specified there too).

Just `/t` or `/topic` in any discord proxy channel will list more such commands
and more info on how to use them.

Last message sent to a discord channel can be [edited using sed-replacement command]
like `s/hoogle/google/` to fix a typo or quickly amend/reword/clarify that last line.\
Or `//del` command can be used to delete it - see ["quick edits/deletes"] section below.

`@silent` prefix-command in messages can suppress user notifications about it
(also [explained below somewhere]).

In special channels like #rdircd.control and #rdircd.debug: send `h` or `help`.\
They can have somewhat long list of supported commands,
e.g. here are some of the commands for #rdircd.control:

- `status` (or `st`) can be used to check on discord and irc connection infos.

- `connect` / `disconnect` (or `on` / `off`) commands can be used to manually
  control discord connection, e.g. for a more one-off usage, or to temporarily
  suppress failed conn warnings while local network is down that way.

- `set irc-disable-reactions yes` - temp-disable discord
  reaction notifications (using `set` command).\
  Or `set -s irc-disable-reactions yes` to make it permanent (`-s/--save`
  flag for saving value to ini config file), or simple `set` without parameters
  to see all general configuration options and their values.

- `rx Block mee6 bot-noise = (?i)^<MEE6>` - temp-block all messages from MEE6 bot.\
  (see [section about this filtering] below, or [more examples of such stuff under tips-and-tricks])

...and there are more of those - type `help` there for full up-to-date info.

[local renames]: #hdr-local_name_aliases
[various discord names]: #hdr-people_s_names_on_discord
[edited using sed-replacement command]: #hdr-quick_edits_deletes_for_just-sent_messages
["quick edits/deletes"]: #hdr-quick_edits_deletes_for_just-sent_messages
[explained below somewhere]: #hdr-_silent_messages_and_other_such_flags
[section about this filtering]: #hdr-custom_filtering_for_all_received_messages
[more examples of such stuff under tips-and-tricks]: #hdr-cut_down_on_various_common_noise

<a name=hdr-_rdircd.monitor_and_rdircd.leftover_channels></a>
### #rdircd.monitor and #rdircd.leftover channels

#rdircd.monitor can be used to see activity from all connected servers -
gets all messages, prefixed by the relevant irc channel name.

#rdircd.monitor.guild (where "guild" is a hash or alias, see above)
is a similar catch-all channels for specific discord server/guild.

#rdircd.monitor.me can be useful, for example, to monitor any private chats
and messages for discord account (see also [Auto-joining channels] example).

#rdircd.leftover and similar #rdircd.leftover.guild channels are like monitor
channels, but skip messages from any channels that IRC client have JOIN-ed,
including e.g. `/join #rdircd.leftover.game-x` hiding that "game-x" discord
msgs from global catch-all #rdircd.leftover, but not counting #rdircd.monitor
channels (i.e. joining them doesn't affect "leftover" ones in any way).

#rdircd.voice is a channel similar to #rdircd.monitor, but only catching
voice-chat event notices, to be able to track those in a timely manner.

These channels can be ignored if not needed, or disabled entirely by setting
e.g. `chan-monitor` to an empty value under \[irc\] ini config-file section.
For example, per-discord voice-activity channels are default-disabled there.

Configuration file also has \[unmonitor\] section for an optional list
of channel-names to ignore in monitor/leftover channels, for example:

``` ini
[unmonitor]
# All filters are applied to channel names and are case-insensitive
Ignore this particular "bot-commands" channel = game-X.bot-commands
skip forum threads in "game-X" guild = glob:game-X.forum.=*
"wordle" threads in any guild (and chans ending in .wordle) = glob:*.wordle
Don't show threads in any forum-like channels = re:^[^.]+\.(forum|discuss)\.=.*
disregard all voice-chat stuff = glob:*.vc
```

Keys (as in part before "=") in such config section are ignored, and can be
anything, e.g. comments explaining the patterns (like in example above), while
values are either exact channel names (with discord prefix, optional #-prefix),
or a "glob:"/"re:"-prefixed glob / regexp pattern ([shell-like globs] or
[python regexps]), written as `<some-key/comment> = glob:<wildcard-pattern>`
or `<some-key/comment> = re:<regexp-pattern>` lines - see examples just above.

Channel names matched by those filters will be dropped from monitor-channels,
so this can be used to define a list of spammy things that you don't care about
and don't want to see even there.

"unmonitor" (or "um") command in #rdircd.control can add/remove such filters
on-the-fly anytime. See also `match-counters` config option to keep track of
whether specific rule(s) are still needed/being-used.

Messages in monitor-channels are limited to specific length/lines,
to avoid excessive flooding by long and/or multi-line msgs.
"len-monitor" and "len-monitor-lines" parameters under \[irc\] config
section can be used to control these limits,
see ["./rdircd --conf-dump-defaults" output] for their default values.
There are also options to change name format of monitor channels.

[shell-like globs]: https://docs.python.org/3/library/fnmatch.html
[python regexps]: https://docs.python.org/3/library/re.html
["./rdircd --conf-dump-defaults" output]: rdircd.defaults.ini

<a name=hdr-people_s_names_on_discord></a>
### People's names on discord

On IRC, everyone has one name, but that's [not the case with Discord],
where each user can have following names:

- `login` - discord "username", uniquely identifying every user.
- `display` - "display name" set by the user in discord account settings, not unique.
- `nick` - server and friend "nicknames", set in discord server settings, not always by you.

`login` is closest concept to IRC nicknames, as it's globally-unique,
consistent, short, ascii-only, and can be used by setting
`name-preference-order = login` option in \[discord\] section (not the default).

Official discord clients display other names first, which is why
`name-preference-order` option defaults to `nick display login` value,
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
so if it gets too silly and maddening, set `name-preference-order = login`
to use unique consistent IRC-friendly nicks for everyone instead.

IRC `/who` command or `/topic info` can help translating between these names,
for example `/t info john1234` can be used to print info for that name/login
in the channel buffer, which should include all users with partial match of that
name on that specific discord, while `/who` command searches all joined discords.

[not the case with Discord]:
  https://support.discord.com/hc/en-us/articles/12620128861463-New-Usernames-Display-Names

<a name=hdr-local_name_aliases></a>
### Local Name Aliases

(more like "renames" than "aliases", as old names don't continue to work for these)

Can be defined in the config file to replace hash-based discord prefixes or server
channel names with something more readable/memorable or meaningful to you:

``` ini
[renames]
guild.jvpp = game-x
guild.sn3y = log-bot
guild.sn3y.chan-fmt = logs/{name}.log
chan.some-long-and-weird-name = weird
chan.@710035588048224269 = general-subs
user.noname123 = my-pal-bob
user.@123980071029577864 = joe
```

This should:

- Turn e.g. #jvpp.info into #game-x.info - lettersoup guild-id to more
  meaningful prefix. This will apply to all channels in that discord -
  "guild" renames.

- Change format for channel names of "sn3y" discord from something like
  #sn3y.debug to #logs/debug.log - changing of channel name format.

  Format template uses [python str.format syntax] with "name" (channel name)
  and "prefix" (guild prefix - will be "log-bot" in this example) values.
  Default format is `{prefix}.{name}`.

  This format option does not affect monitor/leftover channel name(s)
  (e.g. #rdircd.monitor.log-bot or #rdircd.leftover.game-x) -
  see "chan-monitor-guild" and "chan-leftover-guild" options under \[irc\]
  section for changing that.

- Rename that long channel to have a shorter name (retaining guild prefix) -
  "chan" renames.

  Note that this affects all guilds where such channel name exists, and source name
  should be in irc format, same as in /list, and is rfc1459-casemapped (same as on irc).

- Rename channel with id=710035588048224269 to "memes" (retaining guild prefix) -
  "chan" renames using @channel-id spec.

  That long discord channel identifier (also called "snowflake") can be found by
  typing `/t info` topic-command in corresponding irc channel, and can be used
  to refer to that specific channel, i.e. renaming this one #general on this one
  discord server instead of renaming all #general channels everywhere.

  This is especially useful when two channels have same exact name within same
  discord, and normally will be assigned `.<id-hash>` non-descriptive suffixes.

- Rename couple users, referenced by their discord username and id.

  `/t info <nick-or-part-of-it>` command in discord channel or similar `/who`
  irc-command can help to [Lookup Discord IDs], like ones used there.

Currently only listed types of renaming are implemented, for discord prefixes
and channels, but there are also options under \[irc\] section to set names for
system/monitor/leftover and private-chat channels - "chan-sys", "chan-private",
"chan-monitor" and such (see ["./rdircd --conf-dump-defaults" output]).

Set `chan-monitor-guild = {prefix}` there for example, to have #game-x channel be
catch-all for all messages in that discord, without default long #rdircd.monitor.\* prefix.

[python str.format syntax]:
  https://docs.python.org/3/library/string.html#format-string-syntax

<a name=hdr-private_messages_and_friends></a>
### Private messages and friends

Discord private messages create and get posted to channels in "me" server/guild,
same as they do in discord webui, and can be interacted with in the same way as
any other guild/channels (list, join/part, send/recv msgs, etc).

Join #rdircd.monitor.me (or #rdircd.monitor, see above) to get all new
msgs/chats there, as well as relationship change notifications (friend
requests/adds/removes) as notices.

Accepting friend requests and adding/removing these can be done via regular
discord webui and is not implemented in this client in any special way.

See also [Auto-joining channels] section below for an easy way to pop-up
new private chats in the IRC client via invites.

<a name=hdr-discord_channel_threads___forums></a>
### Discord channel threads / forums

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
parent channel (mostly in \[discord\] section, [see --conf-dump-defaults output]):

``` ini
[irc]
thread-chan-name-len = 30

[discord]
thread-id-prefix = =
thread-msgs-in-parent-chan = yes
thread-msgs-in-parent-chan-monitor = no
thread-msgs-in-parent-chan-full-prefix = no
thread-redirect-prefixed-responses-from-parent-chan = yes
...
```

But even with all these disabled, a simple notice should be sent to the channel
when threads are started, so that one won't miss them entirely.

There's no support for creating new threads from IRC, unarchiving old ones or
otherwise managing these, and joining thread channel in IRC doesn't actually
"join thread" in Discord UI (pining it under channel name), but posting anything
there should do that automatically.

[see --conf-dump-defaults output]: rdircd.defaults.ini

<a name=hdr-auto-joining_channels></a>
### Auto-joining channels

"chan-auto-join-re" setting in \[irc\] section allows to specify regexp to match
channel name (without # prefix) to auto-join when any messages appear in them.

For example, to auto-join any #me.\* channels (direct messages),
following regular expression value ([python "re" syntax]) can be used:

``` ini
[irc]
chan-auto-join-re = ^me\.
```

Or to have irc client auto-join all channels, use `chan-auto-join-re = .`\
Empty value for this option (default) will match nothing.

This can be used as an alternative to tracking new stuff via
#rdircd.monitor/leftover channels.

This regexp can be tweaked at runtime using "set" command in #rdircd.control
channel, same as any other values, to e.g. temporary enable/disable this feature
for specific discords or channels.

[python "re" syntax]:
  https://docs.python.org/3/library/re.html#regular-expression-syntax

<a name=hdr-discord_user_mentions></a>
### Discord user mentions

These are `@username` tags on discord, designed to alert someone to direct-ish message.

With default config, when you see e.g. `<Galaxy🌌·Brain> Hi!` and want to
reply highlighting them, sending `Hey @galaxy and welcome` should probably work.
Can also use their full irc nick, to be sure.

How it works: if rdircd matches `msg-mention-re` regexp conf-option against
something in a message being sent (e.g. `@galaxy` @-mention above), that'd be
treated as a "mention", which is either uniquely-matched and translated into a
discord mention in the sent message, or returns an error notice (with nicks that
match that mention ambiguously, if any).

Default value for it should look like this:

``` ini
[discord]
msg-mention-re = (?:^|\s)(@)(?P<nick>[^\s,;@+]+)
```

Which would match any word-like space- or punctuation-separated `@nick`
mention in sent lines.

Regexp ([python "re" syntax]) must have named "nick" group with
nick/username lookup string, which will be replaced by discord mention tag,
and all other capturing groups (i.e. ones without `?:`) will be stripped
(like `@` in above regexp).

Default regexp above should still allow to send e.g. `\@something` to appear
non-highlighted in webapp (and without `\` due to markdown), as it won't be
matched by `(?:^|\s)` part due to that backslash prefix.

As another example, to have classic irc-style highlights at the start of the
line, regexp like this one can be used:

    msg-mention-re = ^(?P<nick>[^\s,;@+]+)(: )

And should translate e.g. `mk-fg: some msg` into `@mk-fg some msg`
(with @-part being mention-tag). Trailing space is included in regexp there
to avoid matching URL links.

To ID specific discord user, "nick" group will be used in following ways:

- Case-insensitive match against all recent guild-related irc names
  (message authors, reactions, private channel users, etc).
  `user-mention-cache-timeout` config option controls "recent" timeout.

- Lookup unique name completion by prefix, same as discord does in webui for
  auto-completion after @ is typed.

- If no cached or unique match found - error notice will be issued
  and message not sent.

Such strict behavior is designed to avoid any unintentional mis-translations,
and highlighting wrong person should generally only be possible via misspelling.

Related `msg-mention-re-ignore` option (regexp to match against full capture
of pattern above) can also be used to skip some non-mention things from being
treated as such, that'd otherwise be picked-up by first regexp, stripping
capturing groups from them too, which can be used to e.g. undo escaping.

Set `msg-mention-re` to an empty value to disable all this translation entirely.

Note that discord user lists can be quite massive (10K+ users), are not split
by channel, and are not intended to be pre-fetched by the client, only queried
for completions or visible parts, which doesn't map well to irc, hence all this magic.

<a name=hdr-quick_edits_deletes_for_just-sent_messages></a>
### Quick edits/deletes for just-sent messages

Similar to [Discord user mentions] above, there's a special regexp-option that
matches commands to be interpreted as edit or removal of last message sent to
this channel.

Default regexps look something like this (check [--conf-dump-defaults] jic):

``` ini
[discord]
msg-edit-re = ^\s*s(?P<sep>[/|:])(?P<aaa>.*)(?P=sep)(?P<bbb>.*)(?P=sep)\s*$
msg-del-re = ^\s*//del\s*$
```

They match sed/perl/irc-like follow-up amendment lines like `s/spam/ham/`, and
`//del` line, which will never be sent to discord, only used as internal commands.

(`s|/some/path|/other/path|` and
`s:cat /dev/input/mouse0 | hexdump:hexdump </dev/input/mouse0:`
syntaxes are also allowed by default edit-regexp, just like with [sed], for
easier handling of common stuff like paths, which can have these chars in them)

Both commands matched by these operate on last message sent by rdircd to the
same discord channel, with `//del` simply removing that last message, and edit
running [python re.sub()] ([PCRE-like]) regexp-replacement function on it.

"msg-edit-re" regexp option value matching sed-like command must have named
"aaa" and "bbb" groups in it, which will be used as pattern and replacement
args to re.sub(), respectively.

If edit doesn't seem to alter last-sent message in any way, it gets discarded,
and also generates IRC notice response, to signal that replacement didn't work.

Successful edit/deletion should also be signaled as usual by discord,
with \[edit\] or such prefix (configurable under \[irc\] section).

Any older-than-last messages can be edited through Discord WebUI - this client
only tracks last one for easy quick follow-up oops-fixes, nothing more than that.

[Discord user mentions]: #hdr-discord_user_mentions
[--conf-dump-defaults]: rdircd.defaults.ini
[sed]: https://en.wikipedia.org/wiki/Sed
[python re.sub()]: https://docs.python.org/3/library/re.html#re.sub
[PCRE-like]: https://en.wikipedia.org/wiki/Perl_Compatible_Regular_Expressions

<a name=hdr-_silent_messages_and_other_such_flags></a>
### @silent messages and other such flags

Somewhat similar to quick edits/deletes above, "msg-flag-silent-re" option is
there to match/remove "@silent" prefix in messages (by default), which disables
sending discord push notifications for it, same as with the official client.

That and similar message flags on incoming messages are not represented
in any way, as they don't seem to be relevant for an irc client anyway.

<a name=hdr-custom_replacements_blocks_in_outgoing_m.NzCf></a>
### Custom replacements/blocks in outgoing messages

Config can have a \[send-replacements\] section to block or regexp-replace
parts of messages sent (by you) from IRC on per-discord basis.

This can be used to add discord-specific tags, unicode shorthands, emojis,
stickers, block/replace specific links or maybe even words/language before
proxying msg to discord.

Here's how it can look in the ini file(s):

``` ini
[send-replacements]

*.unicode-smiley = (^| ):\)( |$) -> \1😀\2
*.twitter-to-nitter = ^(https?://)((mobile|www)\.)?twitter\.com(/.*)?$ -> \1nitter.ir\4

guildx.never-mention-rust! = (?i)\brust\b -> <block!>
guildx.localize-color-word = \bcolor(ed|i\S+)\b -> colour\1
```

Where each key has the form of `discord-prefix> "." comment`,
with a special `*` prefix to apply rule to all discords, while values
are `regexp " -> " <replacement_or_action` with one special `<block!>`
action-value to block sending msg with error-notice on regexp match.
"comment" part of the key can be any arbitrary unique string.

So when sending e.g. `test :)` msg on IRC, discord will get `test 😀`.

Same as with other regex-using options, regexps have python "re" module syntax,
applied via [re.sub()] function, using raw strings from config value as-is,
without any special escapes or interpretations.

Replacements are applied in the same order as specified, but with `*` keys
preceding per-discord ones, and before processing to add discord tags, so anything
like @username that can normally be typed in messages can be used there too.

#rdircd.control channel has "repl" command to edit these rules on-the-fly.

[re.sub()]: https://docs.python.org/3/library/re.html#re.sub

<a name=hdr-custom_filtering_for_all_received_messages></a>
### Custom filtering for all received messages

If you join #rdircd.monitor channel, see - for example - a message like this:

    <helper-bot> #pub.welcomes :: Welcome!

...and think "don't want to see messages like that again!" -
config files' \[recv-regexp-filters\] section or corresponding "rx"
command in #rdircd.control channel can help.

Depending on what "messages like that" means, here are some ways to filter those out:

``` ini
[recv-regexp-filters]
discard msgs from this bot = ^<helper-bot>
ignore all msgs in that channel of that discord = ^\S+ #pub\.welcomes ::
drop all msgs from "pub" discord = ^\S+ #pub\.
no messages from #welcomes channels of any discord pls = ^\S+ #\w+\.welcomes ::
never see "Welcome!" message-text again!!! = ^\S+ #\S+ :: Welcome!$
some combination of the above = (?i)^<helper-bot> #\w+\.welcomes ::
...
```

(tweak e.g. [last example on regex101.com] for more hands-on understanding)

Lines in that section have the usual `<key> = <regexp>` form, where `<key>`
part can be anything (e.g. comment to explain regexp, like in examples above),
and `<regexp>` value is a regular expression to match against the message in
`<user> #discord.channel-name :: message text` format like that helper-bot
msg presented above, and same as can be seen in monitor-channels.

Any message received from discord will be matched against all regexps in order,
stopping and discarding the message everywhere on first (any) match.
So it might be a good idea to write as precise patterns as possible, to avoid
them matching anything else and dropping unrelated messages accidentally.

Same as with some other conf options, basic knowledge of regular expressions
might be needed to use such filters - [here's a link to nice tutorial on those]
(though there are 100s of such tutorials on the web).

Particular regexps here use PCRE-like [python re syntax], with re.DOTALL
flag set (`.` matches newlines in multiline messages).
I'd also recommend commonly adding `(?i)` case-insensitive-match flag,
as IRC nicks and channel names ignore character case and can be displayed
in misleading/inprecise ways in the client.

More random examples of \[recv-regexp-filters\], incl. more advanced CNF weirdness:

``` ini
[recv-regexp-filters]
disregard wordle thread there = ^\S+ #pub\.general\.=w8mk\.wordle ::
ignore "wordle" threads everywhere = ^\S+ #\S+\.=\w{4}\.wordle ::
activity-level bots are annoying = (?i) advanced to level \d+[ !]
gif replies of YY in ZZ = (?i)^<YY> #ZZ\.\S+ :: (-- re:[^\n]+\n)?\[att\] .*/image\d\.gif\?

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
```

Pretty much anything can be matched with clever regexps, so CNF-logic stuff
like in last examples is seldom useful, but might still be simpler than
expressing arbitrary ordering or negation in regexps.

See also `match-counters` config option to keep track of whether specific
rule(s) are still needed/being-used.

[last example on regex101.com]: https://regex101.com/r/VMvyfS/2
[here's a link to nice tutorial on those]: https://github.com/ziishaned/learn-regex
[python re syntax]: https://docs.python.org/3/howto/regex.html

<a name=hdr-lookup_discord_ids></a>
### Lookup Discord IDs

Mostly useful for debugging - `/who` command can resolve specified ID
(e.g. channel_id from protocol logs) to a channel/user/guild info:

- `/who #123456` - find/describe channel with id=123456.
- `/who %123456` - server/guild id info.
- `/who @123456` - user id lookup.

All above ID values are unique across Discord service within their type.

- `/who @John·Mastodon` - user IRC nick or name/login lookup.

    Queries all joined discords for that name, and can return
    multiple results for same or similar non-unique names.
    Can be useful to check exact nick/display/login names
    corresponding to an IRC name, or other user info.

- `/who *665560022562111489` - translate discord snowflake-id to date/time.

Results of all these commands should be dumped into a server buffer
(not into channels), regardless of where they were issued from.

In irc channels corresponding to ones on discord, `/topic info` command
(often works as shortened `/t info` in clients too) can be used to print
more information about linked discord channel and its server/guild.

`/t info <username>` can also print info on user in that discord
(unlike `/who @<username>` which looks the name up in all connected discords),
for example `/t info john` will print info for anyone with "john" in the name.

Usernames in these queries can match exact irc name or discord username,
in which case that result is returned, or otherwise more general server-side
lookup is made, which can return matches in any type of discord name(s)
(see [People's names on discord] for more info on those).

<a name=hdr-channel_name_disambiguation></a>
### Channel name disambiguation

Discord name translation is "mostly" deterministic due to one exception -
channels with same (casemapped) IRC name within same server/guild,
which discord allows for.

When there is a conflict, chan names are suffixed by `.<id-hash>`
(see chan-dedup-\* config options), to allow using both channels through IRC.
Renaming conflicting channels on Discord will rename IRC chans to remove
no-longer-necessary suffixes as well. Such renames affect thread-channels too.

Note that when channels are renamed (including name conflicts),
IRC notice lines about it are always issued in affected channels,
and any relevant monitor/leftover channels, topic should be changed
to reflect that old-name channel is no longer useful, and posting msgs
there should emit immediate warnings about it.

<a name=hdr-osc_8_hyperlinks_for_terminal_irc_clients></a>
### OSC 8 hyperlinks for terminal IRC clients

Discord CDN URLs for attachments can end up being quite long with
same host, long discord/channel IDs in there, then actual filename,
and `?ex=...&is=...&hm=...` trail of CDN parameters after that.

Many Linux IRC clients run in Terminal Emulators though, which often support
[OSC 8 terminal hyperlink standard], so can display clickable links in a much
more compact and readable form.

For example, this attachment URL to a Discord CDN:

    https://cdn.discordapp.com/attachments/1183893786254905414/1206216641877377024/20240211_My_Cat_Photo.jpg?ex=65db33c9&is=65c8bec9&hm=9c1dbecbfb2f9edf2302ec078f5e62fffa7f8c2f32e5cd6e3563ae25d8a356e1&

Can be displayed in a terminal like this instead: [20240211_My_Cat_Photo.jpg]\
I.e. same as how one would see hyperlinks displayed in a browser.

This is disabled by default, but if you use terminal IRC client that might
support those, set `terminal-links = yes` option in config file or via `set`
command in an #rdircd.control channel to try it out.

Adjacent `terminal-links-re` and `terminal-links-tpl` options can be used to
control which part of the link to display as its visible name, which terminal-specific
escape characters to use, and such customization.

[OSC 8 terminal hyperlink standard]:
  https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
[20240211_My_Cat_Photo.jpg]:
  https://cdn.discordapp.com/attachments/1183893786254905414/1206216641877377024/20240211_My_Cat_Photo.jpg?ex=65db33c9&is=65c8bec9&hm=9c1dbecbfb2f9edf2302ec078f5e62fffa7f8c2f32e5cd6e3563ae25d8a356e1&

<a name=hdr-voice_chat_activity_notifications></a>
### Voice chat activity notifications

Discord has voice channels, where in addition to text people can talk verbally,
share camera or screen capture (aka streaming, screen sharing).
IRC protocol does not support anything like this of course, but it can be useful
to get notified when someone starts talking, to hop into different discord client
(e.g. open it in a browser), and use these channels from there.

All IRC channels corresponding to discord voice chats automatically get `.vc`
suffix (unless renamed), and get notice messages about voice activity in there,
but limited to following events, to avoid being too spammy:

- Someone "joins" an empty voice channel to talk there.
- Voice channel becomes empty, i.e. last person leaves.
- When some activity (e.g. join/leave/talk/etc) happens in voice channel
  after configured `voice-notify-after-inactivity` timeout of inactivity
  (i.e. since previous voice-status notification there), default = 20 minutes.

And with additional rate-limit set by `voice-notify-rate-limit-tbf` value,
to notify about up to 5 events in a row, but otherwise no more often than
once in 5 minutes (["token bucket algorithm"] is technically how this
limit is implemented/works).

If description above sounds confusing, here's config tweaks to remove all limits
on voice-activity event notifications - try those, and maybe re-read this section
later if they get too spammy (maybe never!):

``` ini
[discord]
voice-notify-after-inactivity = 0
voice-notify-rate-limit-tbf = 0
```

#rdircd.voice monitor-channel(s) can also be used to only track voice-chat
notifications across discords/channels, potentially filtered via "um" command
in #rdircd.control or \[unmonitor\] in ini config(s).

["token bucket algorithm"]: https://en.wikipedia.org/wiki/Token_bucket

<a name=hdr-highlight_on_incoming_private_messages></a>
### Highlight on incoming private messages

IRC convention is to treat mention of a nickname as a "highlight" - a more
notification-worthy event than a regular channel message, so it might be useful
if messages in private channels did always highlight the nick for IRC client.

`prefix-all-private` option can be used for that:

``` ini
[irc]
prefix-all-private = mynick: \
```

Might also be necessary to either join [monitor/leftover channels] or setup
[auto-joining channels] for new PMs to be received by IRC client at all.

Private chats are not implemented via direct IRC messages for various practical
reasons, i.e. to have everything work via channels, because it works that way on
the discord side, they can have multiple users, to list those easily, to query
topic/history/etc there, and such stuff.

There is a similar `prefix-all` option, to add prefix to all messages,
if `prefix-all-private` doesn't go far enough.

[monitor/leftover channels]: #hdr-_rdircd.monitor_and_rdircd.leftover_channels
[auto-joining channels]: #hdr-auto-joining_channels

<a name=hdr-message_acks_typing_notifications_and_ot.9aX7></a>
### Message ACKs, typing notifications and other events from IRC

By default, \[discord\] `msg-ack=yes` enables sending (delayed) ACKs for received
messages in private chats, so that discord counts those as read and doesn't send
an email notification about them. This can be disabled or adjusted in config file.\
Messages blocked by e.g. \[recv-regexp-filters\] or received when there are
no IRC clients connected don't count.

If IRC client supports [IRCv3 typing notifications] and has these enabled,
rdircd will forward those from discord users/channels by default, which can be
disabled by setting `typing-interval = 0` in \[irc\] configuration section,
or interval/timeout values can be adjusted there to work better for IRC app.

Separate `typing-send-enabled` option controls whether typing notifications
from IRC are sent to a discord channel. It is disabled by default for privacy
reasons, and likely needs to be explicitly enabled in IRC client as well.

Any IRCv3 features like that typing stuff can also be disabled via `ircv3-caps`
option, e.g. if there're problems with them in rdircd or client.

[IRCv3 typing notifications]: https://ircv3.net/specs/client-tags/typing

<a name=hdr-warning_session_auth_rejected_unexpected.ZboG></a>
### WARNING :: Session/auth rejected unexpectedly - disabling connection

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
`ws-reconnect-on-auth-fail = yes` option in \[discord\] ini section,
which will force client to keep reconnecting regardless.

<a name=hdr-captcha-solving_is_required_to_login_for.ls9P></a>
### Captcha-solving is required to login for some reason

Don't know why or when it happens, but was reported by some users in this and
other similar discord clients - see [issue-1] here and links in there.

Fix is same as with [bitlbee-discord] - login via browser, maybe from the same
IP Address, and put auth token extracted from this browser into configuration
ini file's \[auth\] section, e.g.:

``` ini
[auth]
token = ...
```

See "Usage" in README of [bitlbee-discord] (scroll down on that link) for how to
extract this token from various browsers.

Note that you can use multiple configuration files (see `-c/--conf` option) to specify
this token via separate file, generated in whatever fashion, in addition to main one.

Extra `token-manual = yes` option can be added in that section to never
try to request, update or refresh this token automatically in any way.
Dunno if this option is needed, or if such captcha-login is only required once,
and later automatic token requests/updates might work (maybe leave note on
[issue-1] if you'll test it one way or the other).

Never encountered this problem myself so far.

[issue-1]: https://github.com/mk-fg/reliable-discord-client-irc-daemon/issues/1

<a name=hdr-debugging_anything_strange_unknown_or_un.NQDm></a>
### Debugging anything strange, unknown or unexpected

Most likely source of that should be missing handling for some new/uncommon
discord events, or maybe a bug in the code somewhere - either can be reported as
a github issue.

To get more information on the issue (so that report won't be unhelpful "don't work"),
following things can be monitored and/or enabled:

-   Standard error stream (stderr) of the script when problem occurs and whether
    it crashes (unlikely).

    If rdircd is run as a systemd service, e.g. `journalctl -au rdircd` should
    normally capture its output, but there are other ways to enable logs listed just below.

    rdircd shouldn't normally ever crash, as it handles any errors within its own
    loop and just reconnects or whatever, but obviously bugs happen - there gotta
    be some python traceback printed to stderr on these.

-   Find a way to reproduce the issue.

    When something weird happens, it's most useful to check whether it can be
    traced to some specific discord and event there (e.g. some new feature being used),
    or something specific you did at the time, and check whether same thing
    happens again on repeating that.

    That's very useful to know, as then problem can be reproduced with any kind of
    extra logging and debugging aids enabled until it's perfectly clear what's
    going on there, or maybe how to avoid it, if fixing is not an option atm.

-   Join #rdircd.debug channel - any warnings/errors should be logged there.

    Send "help" (or "h") msg to it to see a bunch of extra controls over it.

    Sending "level debug" (or "d") there for example will enable verbose debug
    logging to that channel (can be disabled again via "level warning"/"w"),
    but it might be easier to use log files for that - see below.

-   Enable debug and protocol logs to files.

    In any loaded rdircd ini file(s), add \[debug\] section with options like these:

    ``` ini
    [debug]
    log-file = /var/log/rdircd/debug.log
    proto-log-shared = no
    proto-log-file = /var/log/rdircd/proto.log
    ```

    `/var/log/rdircd` dir in this example should be created and accessible only
    to running rdircd and ideally nothing else, e.g. creating it as:
    `install -m700 -o rdircd -d /var/log/rdircd`

    Such opts should enable those auto-rotating log files, which will have a lot
    of very information about everything happening with the daemon at any time.

    Both of these can also be enabled/controlled and/or queried at runtime from
    #rdircd.debug chan.

    `proto-log-shared` option (defaults to "yes") and be used to send
    discord/irc protocol logging to same log-file or #rdircd.debug channel,
    but it might be easier to have two separate logs, as in example above.

    Log file size and rotation count can be set via `log-file-size`,
    `log-file-count`, `proto-log-file-size`, `proto-log-file-count`
    options - run `rdircd --conf-dump-defaults` to see all those and their
    default values ([rdircd.defaults.ini] has some recent-ish copy too).

    When running with protocol logs repeatedly or over long time,
    `proto-log-filter-ws` option can be handy to filter-out spammy
    uninteresting events there, like GUILD_MEMBER_LIST_UPDATE.

    Note that these files will contain all sorts of sensitive information - from
    auth data to all chats and contacts - so should probably not be posted or
    shared freely on the internet in-full or as-is, but can definitely help to
    identify/fix any problems.

-   Running `/version` IRC-command should at least print something like
    `host 351 mk-fg 22.05.1 rdircd rdircd discord-to-irc bridge` on the first line,
    which is definitely useful to report, if it's not the latest one in this git repo.

Generally if an issue is easy to reproduce (e.g. "I send message X anywhere and
get this error"), it can be reported without digging much deeper for more info,
as presumably anyone debugging it should be able to do that as well, but maybe
info above can still be helpful to identify any of the more non-obvious problems,
or maybe give an idea where to look at for fixing or working around these.


<a name=hdr-random_tips_and_tricks></a>
## Random tips and tricks

Some configuration tweaks that I use, or mentioned in #rdircd on IRC and such.\
Feel free to suggest any other lifehacks to add here.

<a name=hdr-simpler_dm_and_monitor_channel_names></a>
### Simpler DM and monitor channel names

Normally rdircd uses these long strange "#rdircd.monitor" channel name
templates, as well as unnecessary "#me.chat."  prefixes, instead of this:

```
#DMs
#@some-friend
#@some-friend+other-friend+more-ppl
#rdircd
#rdircd.rest
#rdircd.voice
#rdircd.control
#rdircd.debug
#minecraft
#minecraft.general
#minecraft.modding
#minecraft.rest
```

Use these lines in any loaded ini config file to make it work like that:

``` ini
[irc]
chan-monitor = rdircd
chan-leftover = rdircd.rest
chan-monitor-guild = {prefix}
chan-leftover-guild = {prefix}.rest
chan-private = {names}

[renames]
guild.me = DMs
guild.me.chan-fmt = @{name}
```

What these options do, in the same order: rename "#rdircd.monitor" to "#rdircd",
set names for all discord-specific monitor channels to just "{prefix}"
(e.g. "#dm" or "#minecraft"), set private-chat channels to use people's name(s)
without "chat." prefix, rename default "me" guild (private chats) to "DMs",
use simpler @ + name format for any channels there.

Defaults are that way to try to be more explicit and descriptive,
but once you know what all these channels are for, can easily rename
them to something shorter/nicer and more convenient for yourself.

<a name=hdr-change_message_edit_embed_attachment_pre.xxnp></a>
### Change message edit/embed/attachment prefixes to shorter emojis

When message is edited, you normally get something like `[edit] new msg text`,
but it can be `✍️ new msg text` or `📝 new msg text` instead:

``` ini
[irc]
prefix-edit = 📝 \
prefix-embed = 📎.{} \
prefix-attachment = 🖼️ \
prefix-uis = ⚙️ \
prefix-interact = 🤖 \
prefix-poll = 🗳️.{} \
```

Note the "space and backslash" at the end in these options, which is to preserve
trailing spaces in values, from both text editors that strip those and configuration
file parser (which ignores any leading/trailing spaces, unless punctuated by backslash).
`prefix-embed` and poll values need `{}` placeholder for where to put short id/tag.

Alternatively, set-command like `set irc-prefix-edit '✍️ '` can be used in #rdircd.control
to configure and tweak this stuff on-the-fly (or `-s/--save` into config too).

<a name=hdr-cut_down_on_various_common_noise></a>
### Cut down on various common noise

Using discord through IRC can be a bit noisy due to edits or spammy notifications
ending up in various monitor/leftover channels or other un-irc-like features,
which rdircd can help mitigate to some degree, but often doesn't by default,
as it's hard to know what other people actually care about.

Here are some random commands to try out in #rdircd.control channel:

- `um Noise from any bot-channels = re:\.bots?(-.*)?$`
- `um Ignore welcome chans = glob:*.welcomes`
- `um Disregard all voice-chat events = glob:*.vc`
- `um Memes belong in a circus = glob:*.memes`
- `um Make food channels opt-in = glob:*.food`
- `um Internet "politics" can get really spammy = glob:*.politic*`
- `um There're probably better places for porn = glob:*.nsfw`

- `rx MEE6 bot-noise anywhere = (?i)^<MEE6>`
- `rx THX discord: people spamming edits = (?i)^<(person1|person2)> #THX\.\S+ :: \[edit\]`
- `rx NSC: don't care about deletes = ^\S+ #NSC\.\S+ :: --- message was deleted ::`
- `rx NSC/THX: disable reactions here = ^\S+ #(NSC|THX)\.\S+ :: --- reacts:`

- Enable rule-hit counters to check whether these rules are still relevant later:\
    `set discord-match-counters '1d 2d 4d 1w 2w 1mo 2mo runtime'`

    With these enabled, running `um` or `rx` should show `[ rule hits: ... ]`
    under each rule, if there's anything to show (but reset on rdircd restarts!),
    otherwise it's probably safe to drop unused rules to keep lists more tidy.

- Disable "reacts" noise everywhere: `set discord-disable-reactions yes`

- Remove long, confusing and silly nicknames full of unicode junk:\
    `set discord-name-preference-order 'login'`

    If even ascii logins of specific users get annoying, use `[renames]` in
    config to change those locally (see [Local Name Aliases] section for more info):

    ``` ini
    [renames]
    user.somereallylongandsillyloginbecausewhynot = bob
    user.@374984273184829999 = andy
    ```

- Keep threads only as channels, and in #rdircd.leftover.\* and such:\
    `set discord-thread-msgs-in-parent-chan no`

- Don't show voice-chats or "monitor" channels on the `/list`:\
    `set irc-chan-voice ''` `set irc-chan-monitor ''`

All of these examples are not persistent, just to try them out and see, but all
commands used there support `-s` flag to save changed values to last .ini config
file, or it can be done manually as well, if any of these are useful to keep around.


<a name=hdr-links></a>
## Links

There is a good and well-maintained list of alternative clients here:

- [Discord-Client-Encyclopedia-Management/Discord3rdparties]

There are many alt-clients these days, with a lot of churn among them,
and dedicated lists like that are probably best way to discover those.

[Discord-Client-Encyclopedia-Management/Discord3rdparties]:
  https://github.com/Discord-Client-Encyclopedia-Management/Discord3rdparties


<a name=hdr-more_info_on_third-party_client_blocking></a>
## More info on third-party client blocking

As mentioned in the "WARNING" section above, [Bot vs User Accounts]
section in API docs seem to prohibit people using third-party clients,
same as [Discord Community Guidelines].
Also maybe against their [Discord Developer Terms of Service],
but dunno if those apply if you're just using the alt-client.

[Discord Community Guidelines]: https://discord.com/guidelines
[Discord Developer Terms of Service]:
  https://discord.com/developers/docs/policies-and-agreements/developer-terms-of-service

I did ask discord staff for clarification on the matter,
and got this response around Nov 2020:

> > Is third-party discord client that uses same API as webapp, that does not
> > have any kind of meaningful automation beyond what official discord app has,
> > will be considered a "self-bot" or "user-bot"?
> >
> > I.e. are absolutely all third-party clients not using Bot API in violation
> > of discord ToS, period?
> >
> > Or does that "self-bot" or "user-bot" language applies only to a specific
> > sub-class of clients that are intended to automate client/user behavior,
> > beyond just allowing a person to connect and chat on discord normally?
>
> Discord does not allow any form of third party client, and using a client like
> this can result in your account being disabled. Our API documentation
> explicitly states that a bot account is required to use our API: "Automating
> normal user accounts (generally called "self-bots") outside of the OAuth2/bot
> API is forbidden, and can result in an account termination if found."

Another thing you might want to keep in mind, is that apparently it's also
considered to be responsibility of discord admins to enforce its Terms of
Service, or - presumably - be at risk of whole guild/community being shut down.

Got clarification on this issue in the same email (Nov 2020):

> > Are discord server admins under obligation to not just follow discord Terms
> > of Service themselves (obviously), but also enforce them within the server
> > to the best of their knowledge?
> >
> > I.e. if discord server admin knows that some user is in violation of the
> > ToS, are they considered to be under obligation to either report them to
> > discord staff or take action to remove (ban) them from the server?
> >
> > Should failing to do so (i.e. not taking action on known ToS violation)
> > result in discord server (and maybe admins' account) termination or some
> > similar punitive action, according to current discord ToS or internal policies?
>
> Server owners and admin are responsible for moderating their servers in
> accordance with our Terms of Service and Community Guidelines.
> If content that violates our Terms or Guidelines is posted in your server,
> it is your responsibility to moderate it appropriately.

So unless something changes or I misread discord staff position,
using this client can get your discord account terminated,
and discord admins seem to have responsibility to ban/report its usage,
if they are aware of it.

Few other datapoints and anecdotes on the subject:

-   Don't think Discord's "Terms of Service" document explicitly covers
    third-party client usage, but "Discord Community Guidelines" kinda does,
    if you consider this client to be "self-bot" or "user-bot" at least.

    Only thing that matters in practice is likely the actual staff and specific
    server admins' position and actions on this matter, as of course it's a
    private platform/communities and everything is up to their discretion.

-   Unrelated to this client, one person received following warning (2020-01-30)
    after being reported (by another user) for mentioning that they're using
    [BetterDiscord] (which is/was mostly just a custom css theme at the time, afaik):

    ![discord tos violation warning][]

-   In September 2021 there was a bunch of issues with people using different
    third-party clients being asked to reset their passwords daily due to
    "suspicious activity", raised here in [issue-18] (check out other links there too),
    which seem to have gone away within a week.

    At least one person in that issue thread also reported being asked for phone
    account verification for roughly same reason about a week after that, so maybe
    "suspicious activity" triggering for 3p clients haven't really gone away.

-   [Cordless] client developer's acc apparently got blocked for ToS violation when
    initiating private chats. This client doesn't have such functionality, but
    maybe one should be more careful with private chats anyway, as that seem to be
    a major spam vector, so is more likely to be heavily-monitored, I think.

-   In the #rdircd IRC channel, a person mentioned that their discord account got
    some anti-spam mechanism enabled on it, disallowing to log-in without
    providing a phone number and SMS challenge (and services like Google Voice
    don't work there), immediately after they've initiated private chat with
    someone in [Ripcord] client.

    "I contacted support at the time and they just responded that they can't
    undo the phone number requirement once it has been engaged"

    It also seems like Ripcord currently might be trying to mimic official client
    way more closely than rdircd script here does (where latter even sends
    "client"/"User-Agent" fields as "rdircd" and appears that way under Devices in
    User Settings webui), and such similarity might look like Terms of Service
    violation to Discord (modifying official client), instead of Community
    Guidelines violation (third-party client), but obviously it's just a guess
    on my part as to whether it matters.

There are also [some HN comments clarifying Discord staff position in a thread here],
though none of the above should probably be taken as definitive,
since third-party and even support staff's responses can be wrong/misleading or outdated,
and such treatment can likely change anytime and in any direction,
without explicit indication.

[BetterDiscord]: https://github.com/BetterDiscord/BetterDiscord
[discord tos violation warning]: discord-tos-violation-warning.jpg
[issue-18]: https://github.com/mk-fg/reliable-discord-client-irc-daemon/issues/18
[Cordless]: https://github.com/Bios-Marcel/cordless
[Ripcord]: https://cancel.fm/ripcord/
[some HN comments clarifying Discord staff position in a thread here]:
  https://news.ycombinator.com/item?id=25214777


<a name=hdr-api_and_implementation_notes></a>
## API and Implementation Notes

Note: only using this API here, only going by public info, can be wrong,
and would appreciate any updates/suggestions/corrections via open issues.

Last updated: 2024-10-24

-   [Discord API docs] don't seem to cover "full-featured client" use-case,
    likely because such use of its API is explicitly not supported, and is
    against their rules/guidelines (see [WARNING] section above for details).

    It's possible that more recent official OpenAPI spec in
    [discord/discord-api-spec repo] has a more complete documentation though.

-   Discord API protocol changes between versions, which are documented on
    [Change Log page of the API docs].

    Code has API number hardcoded as DiscordSession.api_ver, which has to be
    bumped there manually after updating it to handle new features as necessary.

-   Auth uses undocumented /api/auth/login endpoint for getting "token" value for
    email/password, which is not OAuth2 token and is usable for all other endpoints
    (e.g. POST URLs, Gateway, etc) without any prefix in HTTP Authorization header.

    Found it being used in other clients, and dunno if there's any other way to
    authorize non-bot on e.g. Gateway websocket - only documented auth is OAuth2,
    and it doesn't seem to allow that.

    Being apparently undocumented and available since the beginning,
    guess it might be heavily deprecated by now and go away at any point in the future.

-   There are some unofficial docs for officially-undocumented APIs and quirks:

    - <https://luna.gitlab.io/discord-unofficial-docs/> (+ [litecord] api-testing server)
    - <https://github.com/Merubokkusu/Discord-S.C.U.M/tree/master/docs>
    - <https://discord.neko.wtf/> (maintained by [Abaddon] client dev\[s\])

-   Sent message delivery confirmation is done by matching unique "nonce" value in
    MESSAGE_CREATE event from gateway websocket with one sent out to REST API.

    All messages are sent out in strict sequence (via one queue), waiting on
    confirmation for each one in order, aborting rest of the queue if first one
    fails/times-out to be delivered, with notices for each failed/discarded msg.

    This is done to ensure that all messages either arrive in the same strict
    order they've been sent or not posted at all.

    Discord message-posting API has `enforce_nonce` parameter (since 2024-02-12),
    which allows to retry posting messages safely from duplication, but at the
    moment retries are only performed here on API rate-limiting.

-   Fetching list of users for discord channel or even guild does not seem to be
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

-   Some events on gateway websocket are undocumented, maybe due to lag of docs
    behind implementation, or due to them not being deemed that useful to bots, idk.

-   Discord allows channels and users to have exactly same visible name, which is not
    a big deal for users (due to one-way translation), but still disambiguated irc-side.

-   Gateway websocket [can use zlib compression] (and [zstd in non-browser apps]),
    which makes inspecting protocol in browser devtools a bit inconvenient.

    [gw-ws-har-decode.py] helper script in this repo can be used to decompress/decode
    websocket messages saved from chromium-engine browser devtools
    (pass `-h/--help` option for info on how to do it).

-   Run `./rdircd --test` for info on some extra development/testing helper commands.

    `dev-cmds = yes` under `[debug]` also enables some runtime helpers in #rdircd.control.

-   Adding support for initiating private chats might be a bad idea, as [Cordless]
    dev apparently got banned for that, and since these seem to be main spam vector,
    so more monitoring and anomaly detection is likely done there, leading to
    potentially higher risk for users.

[Discord API docs]: https://discord.com/developers/docs/reference
[discord/discord-api-spec repo]: https://github.com/discord/discord-api-spec/
[Change Log page of the API docs]: https://discord.com/developers/docs/change-log
[litecord]: https://gitlab.com/litecord/litecord
[Abaddon]: https://github.com/uowuo/abaddon
[can use zlib compression]:
  https://discord.com/developers/docs/topics/gateway#encoding-and-compression
[zstd in non-browser apps]:
  https://discord.com/blog/how-discord-reduced-websocket-traffic-by-40-percent
[gw-ws-har-decode.py]: gw-ws-har-decode.py
