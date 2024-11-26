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
			Decode "Save all as HAR with content" dump
				from Discord gateway websocket into JSON lines.
			Reads HAR file either from argument path or stdin, outputs JSON to stdout.

			To save HAR file in chrome/chromium/vivaldi/edge/brave/etc:
			- Open devtools on Discord login screen (F12 key).
			- Open Network tab there, set filter on top of it to "WS" only (websockets).
			- Proceed with logging into discord, perform whatever actions are needed there.
			- In open devtools tab, there should be one websocket connection listed,
				right-click on it and use "Save all as HAR with content" option to save
				all traffic in that session (incl. websocket data) to a HAR file for this script.
			- Pretty-print ws data: ./gw-ws-har-decode.py discord.com.har | jq -C . | less'''))
	parser.add_argument('har_file', nargs='?', help='HAR dump from websocket connection to process.')
	parser.add_argument('-n', '--pick', type=int, metavar='n',
		help='Only pick and print message with specified "ws_seq" sequential number.')
	parser.add_argument('-m', '--pick-to', type=int, metavar='n', help=dd('''
		Modifies -n/--pick option to also print all msgs that come
			after it, up to and including specified one (0 - to the end).'''))
	parser.add_argument('-r', '--run-on-line', metavar='cmd', help=dd('''
		Run specified command on each line (with arguments split on spaces),
			sending JSON to its stdin and passing its stdout/stderr through,
			with line delimiters added in-between. Example: -r 'jq -C .' '''))
	opts = parser.parse_args(sys.argv[1:] if args is None else args)

	line_cmd = None
	if opts.run_on_line:
		import subprocess as sp
		line_cmd = opts.run_on_line.split()

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
	n, buff, buff_end = 1, bytearray(), b'\x00\x00\xff\xff'
	ts_start = ts_last = 0

	for msg in ws_entry['_webSocketMessages']:
		if msg['type'] == 'receive':
			data = base64.b64decode(msg['data'])
			buff.extend(data)
			if data[-4:] != buff_end: continue # partial data
			msg['data'] = inflator.decompress(buff).decode()
			buff.clear()

		msg_print = True
		if opts.pick:
			msg_print = (
				opts.pick == n if opts.pick_to is None
				else opts.pick <= n <= (opts.pick_to or 2**30) )
		if msg_print:
			data = json.loads(msg['data'])
			msg_line = dict(
				ws_seq=n, ws_t=msg['type'], ws_op=msg['opcode'],
				ws_ts=msg['time'],
				ws_ts_diff=ts_last and msg['time'] - ts_last,
				ws_ts_rel=ts_start and msg['time'] - ts_start,
				ws_data=data )

			if not line_cmd: json.dump(msg_line, sys.stdout)
			else:
				print(f'\n\n\n---------- -=msg:{n} ----------', flush=True)
				sp.run(line_cmd, input=json.dumps(msg_line).encode())
			print(flush=True)

		ts_last = msg['time']
		if not ts_start: ts_start = ts_last
		n += 1

if __name__ == '__main__':
	try: sys.exit(main())
	except BrokenPipeError: # stdout pipe closed
		os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
		sys.exit(1)
