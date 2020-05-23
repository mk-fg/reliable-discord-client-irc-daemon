#!/usr/bin/env python

import os, sys, zlib, json, base64

p_err = lambda tpl,*a,**k: print(tpl, *a, **k, file=sys.stderr, flush=True)

def main(args=None):
	import argparse, textwrap
	dd = lambda text: (textwrap.dedent(text).strip('\n') + '\n').replace('\t', '  ')
	fill = lambda s,w=90,ind='',ind_next='  ',**k: textwrap.fill(
		s, w, initial_indent=ind, subsequent_indent=ind if ind_next is None else ind_next, **k )

	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawTextHelpFormatter,
		description=dd('''
			Decode "Save all as HAR with content"' dump
				from Discord gateway websocket into JSON lines.
			Reads HAR file either from argument path or stdin, outputs JSON to stdout.

			To save HAR file in chromium/brave/etc:
			- Open devtools on Discord login screen (F12 key).
			- Open Network tab there, set filter on top of it to "WS" only (websockets).
			- Proceed with logging into discord, perform whatever actions are needed there.
			- In open devtools tab, there should be one websocket connection listed,
				right-click on it and use "Save all as HAR with content" option to save
				all traffic in that session (incl. websocket data) to a HAR file for this script.
			- Pretty-print ws data: ./gw-ws-har-decode.py discord.com.har | jq -C . | less'''))
	parser.add_argument('har_file', nargs='?', help='HAR dump from websocket connection to process.')
	opts = parser.parse_args(sys.argv[1:] if args is None else args)

	src = sys.stdin if not opts.har_file else open(opts.har_file)
	try: dump = json.load(src)
	finally:
		if src is not sys.stdin: src.close()

	ws_entry = None
	for entry in dump['log']['entries']:
		try:
			if not entry['request']['url'].startswith('wss://'): continue
		except: continue # any other entry types
		if ws_entry:
			url = ws_entry['request']['url']
			p_err(f'More than one wss:// connection detected, discarding: {url}')
		ws_entry = entry
	if not ws_entry: parser.error('No wss:// connections found within HAR file')

	inflator = zlib.decompressobj()
	buff, buff_end = bytearray(), b'\x00\x00\xff\xff'

	ts_start = ts_last = 0
	for msg in ws_entry['_webSocketMessages']:
		if msg['type'] == 'receive':
			data = base64.b64decode(msg['data'])
			buff.extend(data)
			if data[-4:] != buff_end: continue # partial data
			msg['data'] = inflator.decompress(buff).decode()
			buff.clear()
		data = json.loads(msg['data'])
		msg_line = dict(
			ws_t=msg['type'], ws_op=msg['opcode'],
			ws_ts=msg['time'],
			ws_ts_diff=ts_last and msg['time'] - ts_last,
			ws_ts_rel=ts_start and msg['time'] - ts_start,
			ws_data=data )
		ts_last = msg['time']
		if not ts_start: ts_start = ts_last
		json.dump(msg_line, sys.stdout)
		sys.stdout.write('\n')

if __name__ == '__main__': sys.exit(main())
