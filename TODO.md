Loose suggestions, ideas and to-fix bugs mentioned in #rdircd and such.

- Add option to do multiline pasting somehow
   current idea is to make a re for start/stop marker line, and make everything in-between multiline
   can implement draft/multiline ircv3 support instead

- Use /me format for reactions, to look like
  `* somenick reacts @ othernick :chk: <time/msg-context?>`

- More options to replay msgs in channels.

    - Add "/t log" replay with an msg-count limit instead of date/time, via `/mesages?limit=N`.
    - Might be useful to have a separate "last msg sent by me" state for chats.
    - Ideally have names for these states, instead of non-obvious numbering.
    - Command to query/replay history since some last state in all joined channels.

- Make commands with options in control-channel reject args that look like commands (likely typos).

- Channel/guild renames should be applied on rdircd config-reload/sighup - needs testing.

    Ideally also send channel rename notifications (and do whatever invites) to connected clients.

- Use `enforce_nonce` API parameter to retry sending msgs reliably, instead of delivery errors.

- IRCv3 MARKREAD can be used for smarter PM ACKs - https://ircv3.net/specs/extensions/read-marker

- Add DCC, filedir, maildir, http-served-dir or some other mechanism to
  pickup/add discord-cdn attachments to messages.

- Test changing password, make error messages from that more comprehensible, if possible.

    Connecting with old token might be giving some special unhandled errors.

- Echo messages sent from IRC back there if client haven't joined channel to which those were sent.

    - Intended for "/msg #channel ..." usage in monitor/leftover channels, to see sent msg there.
    - Also make sending "#chan msg" in monitor channels pass it through to a channel, w/o /msg.

    General idea is to use channel names as nicks in monitor channels, maybe with opt to remove #.

- Send PART for channel users after some timeout expires - inverse of irc-names-join option.

- Change all regexp options to allow exclude-patterns in them uniformly.

    So that ideally any regexp in config can be a backwards-compatible CNF of regexps.

- Add channel name regexp-replacements to `[renames]`, useful when bot activity-indicators are used there.

- Implement replies to cached recent messages.

- Handle `message_poll_vote` (individual votes) similar to reacts,
  with auto-fetched poll-msg cache to print answer text and vote-number fallback.

- In PM channels and such chats with pre-populated users, @user mentions don't seem to work.

- Add command to #rdircd.debug to disable debug logs to stderr/file,
  similar to how protocol logging is controlled there,
  and/or trigger these changes on "set" for corresponding opts in control-channel.

- Add debug command/signal/etc to raise exception, to allow user to test how those are handled,
  and where info about those ends up.

- Make IRC client auto-join channels after their renames, if it was joined to the old one.

- "Expected msg media info parsed to empty line" an such errors should print discord.channel info.

    To print discord/channel name at least (instead of message-id and small part of json),
    so that it'd be apparent what you might be missing, or if it's some irrelevant bot-channel.

- Check for cache-related memleaks, and/or write a note on how to debug those.

    Maybe have user-friendly helper code for this, e.g. to check allocated objects,
    compare vs cache size, report whatever's holding refs to those.

- "Detected persistent discord server connection failures at max delay between attempts" is repeated.

    ```
    [10:28:45] -core- rdircd.discord WARNING :: Detected persistent discord server connection failures at max delay between attempts - there is likely some persistent problem, see info/debug/protocol logs for details
    [10:41:45] -core- rdircd.discord WARNING :: Detected persistent discord server connection failures at max delay between attempts - there is likely some persistent problem, see info/debug/protocol logs for details
    [10:54:46] -core- rdircd.discord WARNING :: Reconnecting to discord faster than 1800:6, can be persistent problem, see info/debug/protocol logs for details
    [11:07:47] -core- rdircd.discord WARNING :: Detected persistent discord server connection failures at max delay between attempts - there is likely some persistent problem, see info/debug/protocol logs for details
    [11:20:48] -core- rdircd.discord WARNING :: Detected persistent discord server connection failures at max delay between attempts - there is likely some persistent problem, see info/debug/protocol logs for details
    ```

    Should probably be repeated less often at least. Not sure if might've fixed it already.

- Rename channel `chan` -> `chan🎄`, then `chan🎄` -> `chan🎄🎁`.

    Might be lost from /list after multiple renames - check this sequence specifically.

- Add option and/or topic-command to write channel name(s) into config, to lock their names against renaming.

- Add special "discord-state" if rdircd isn't trying to reconnect, not just "disconnected" or such.

- Use `update_presence` op=3 event instead of sending protobuff for this.

    https://github.com/sparklost/endcord/blob/main/endcord/gateway.py

- Option to warn on "been offline for >5m" threshold, instead of warnings about reconnect frequency.

    Also maybe an option to indicate when "disconnected for >1 attempt or >10s" (configurable).

    Can indicate via channel topics or some other irc mechanism which would be easier to silence in clients.

- Test/fix interop with alt discord implementations, like spacebar.chat.

- Keep IRC state for all joined channels, to either (A) replay msgs on IRC reconnect,
  or (B) issue notice about missed msgs there.

- Check if reconnection attempts stop on e.g. http-4xx errors for gw token and such,
  instead of gateway socket disconnects/errors.

- Delay cmd_status() with presence indication until after discord is connected.

    If it's set to be online, but not yet connected,
    it might not have valid/tested token for this yet either.

- Match /me messages from *...* in discord ones (from using /me in WebUI),
  maybe check if message json has something in it about this too.

- Add channel name regexp-replacements to [renames], e.g. `name = name.replace('🔵', '')`.

- Add support for zstd gateway-websocket compression - should be supported in recent python stdlib.

- Dockerfile can have a shebang - something like this:

    `#!/usr/bin/env -S bash -c "docker run -p 8080:8080 -it --rm \$(
    docker build --progress plain -f \$0 . 2>&1 | tee /dev/stderr | grep -oP 'sha256:[0-9a-f]*')"`
