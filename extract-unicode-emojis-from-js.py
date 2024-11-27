#!/usr/bin/env python3

import os, sys, re, json, pathlib as pl

err_fmt = lambda err: f'[{err.__class__.__name__}] {err}'
p_err = lambda *a: print(*a, file=sys.stderr, flush=True) or 1

def parse_up(data, n, d):
	'Parse JSON data to until beginning or end of an array/object that n is in'
	st = type('State', (object,), dict(q=False, obj=0, arr=0))
	while 0 < n <= len(data):
		n += d
		# if d > 0: print(f'{n:,d} [ {data[n]} ] {st}')
		if (c := data[n]) == '"':
			if st.q:
				q, m = 0, n-1
				while data[m] == '\\':
					q += 1; m -= 1
					if m == 0: break
				if q and q&1: continue # escaped quote-char
			st.q = not st.q; continue
		if st.q: continue
		if c == '{': st.obj += d
		elif c == '}': st.obj -= d
		elif c == '[': st.arr += d
		elif c == ']': st.arr -= d
		else: continue
		if st.obj < 0 or st.arr < 0: return n
	raise LookupError('No opening array/object brace found')

def main(argv=None):
	import argparse, textwrap
	dd = lambda text: re.sub( r' \t+', ' ',
		textwrap.dedent(text).strip('\n') + '\n' ).replace('\t', '  ')

	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawTextHelpFormatter, description=dd('''
			Parse current list of unicode emojis like :smile: that discord
				auto-translates in messages from a saved web.<something>.js file,
				printing names of all emojis in there, one per line.
			This is intended to generate rdircd.unicode-emojis.txt.gz list-file,
				to not lookup specific :something-something: as discord-custom emoji,
				and leave as-is, without signaling error if it's not found in a discord.

			To save input file for this script using web browser and Discord WebUI:
			- Open Discord WebUI on any channel, open webdev tools using F12 key.
			- Go to Network Tab in webdev tools, filter for All requests there.
			- Open emoji-selection in WebUI's input box for sending new message.
			- This will create emoji-loading requests in Network Tab, right-click on any.
			- Open initiator JS for an image-loading request, save it to a file.'''))

	parser.add_argument('web_js', help=dd('''
		JS file used to load/insert emoji into messages by discord web client.
		All emoji names found in it will be printed one per line.'''))
	opts = parser.parse_args(sys.argv[1:] if argv is None else argv)

	em_names, data = set(), pl.Path(opts.web_js).read_text()
	n, em_keys = 0, 'names surrogates unicodeVersion'.split()
	while (n := data.find('"surrogates":', n)-1) > 0:
		a, b = parse_up(data, n, -1), parse_up(data, n, 1) # single emoji spec
		a, b = parse_up(data, a, -1), parse_up(data, b, 1) # up to emoji list
		data_json, fix_esc = data[a:b+1], list()
		# print(f'n={n:,d} span={b-a:,d} [ -{n-a:,d} +{b-n:,d} ]')
		try:
			# Convert non-ascii latin-1 single-byte escapes like \xf1 to \u00f1 for JSON
			for m in re.finditer(r'(?<!\\)\\x([0-9a-f]{2})', data_json):
				if (cn := int(m[1], 16)) >= 128: fix_esc.append((m.start(), m.end(), cn))
			for ca, cb, cn in reversed(fix_esc):
				data_json = data_json[:ca] + json.dumps(chr(cn))[1:-1] + data_json[cb:]
			for em in json.loads(data_json):
				assert len(set(em).intersection(em_keys)) == len(em_keys)
				em_names.update(em.get('names') or list())
				for em in em.get('diversityChildren') or list():
					em_names.update(em.get('names') or list())
		except Exception as err:
			err_data, sn = data_json, 80
			p_err(f'ERROR: Failed to parse should-be-json chunk - {err_fmt(err)}')
			if (dn := len(err_data)) > sn: p_err( '  trunc chunk'
				f' [{a}-{b} {sn}/{dn:,d}] :: ' + err_data[:sn//2+1] + ' ... ' + err_data[-sn//2:] )
			else: p_err(f'  full chunk [{a}-{b}] :: {err_data}')
			if isinstance(err, json.JSONDecodeError) and (m := re.search(r' \(char (\d+)\)$', str(err))):
				n = int(m[1]); p_err( '  JSON error spot'
					f' {repr(err_data[n-5:n+5])} in :: ...' + err_data[n-sn//2:n+sn//2+1] + '...' )
		n = b

	for em in sorted(em_names): print(em)

if __name__ == '__main__':
	try: sys.exit(main())
	except BrokenPipeError: # stdout pipe closed
		os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
		sys.exit(1)
