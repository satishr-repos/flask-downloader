from __future__ import unicode_literals
import youtube_dl
import argparse
import pprint
import os
import string
import random

class MyLogger(object):
	def debug(self, msg):
		print(msg)

	def warning(self, msg):
		print(msg)

	def error(self, msg):
		print(msg)

def my_hook(d):
	if d['status'] == 'finished':
		print(f"downloaded {d['filename']} with {d['total_bytes']}, now converting ...")

def do_extract_info(url):

	OUTPUT_PATH = os.path.join(os.getcwd(), os.path.join('..','videos'))
	outfile = os.path.join(OUTPUT_PATH, '%(id)s.%(ext)s')

	"""Extract a video url."""
	params = {
		'format': 'bestvideo+bestaudio/best',
		'outtmpl': outfile,
		'writeinfojson': True,
		'writesubtitles': False,
		'noplaylist': True,
		'subtitlesformat': 'srt/ass/vtt/best',
	}

	try:
		info = youtube_dl.YoutubeDL(params).extract_info(url, download=False)
	except :
		print('Exception during operation')
		return { 'raw' : None }

	assert 'formats' in info or info.get('direct'), \
		'Your url cannot be processed correctly'

	title = (info.get('title') or '').strip()
	stitle = ''.join(filter(lambda x: x in string.printable, title))

	info['title'] = stitle

	if 'description' in info:
		info.pop('description')

	for fmt in info['formats']:
		if 'http_headers' in fmt:
			fmt.pop('http_headers')
		if 'url' in fmt:
			fmt.pop('url')
		if 'manifest_url' in fmt:
			fmt.pop('manifest_url')

	return {
		'raw'	: info
	} 

def generate_filename(audio):

	# initializing size of string  
	N = 8
  
	# using random.choices() 
	# generating random strings  
	name = ''.join(random.choices(string.ascii_lowercase +
					string.digits, k = N)) 

	name += '.mp4' if audio == False else '.mp3' 

	filepath = os.path.join('out', name)
	#filepath = name

	return filepath

def do_download(url, quality, audio_only=False, playlist=False):

	outfile = generate_filename(audio_only)

	ydl_opts = {
		#'format': 'bestaudio/best',
		#'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
		#'format' : 'bestvideo[height<=480]+bestaudio/best[height<=480]',	
		#'keepvideo' : True,
		#'postprocessors': [{
		#	'key': 'FFmpegExtractAudio',
		#	'preferredcodec': 'mp3',
		#	'preferredquality': '192',
		#}],
		'restrictfilenames' : True,
        'writeinfojson': True,
        'writesubtitles': False,
		'noplaylist': True,
        'subtitlesformat': 'srt/ass/vtt/best',
		'outtmpl': outfile,
		'logger': MyLogger(),
		'progress_hooks': [my_hook],
	}

	list_fmts = {
		'format': 'bestaudio/best',  # choice of quality
		'extractaudio': True,        # only keep the audio
		'audioformat': "mp3",        # convert to mp3
	}

	postproc = {
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192',
					}]
				}

	if playlist == True:
		ydl_opts.pop('noplaylist')

	if audio_only == True:
		ydl_opts.update(list_fmts)
		ydl_opts.update(postproc)
	else:
		if quality == 'auto':
			fmt = f'bestvideo[ext=m4a]+bestaudio[ext=m4a]/best[ext=m4a]/best'
		else:
			qual = int(quality)
			fmt = f'bestvideo[ext=m4a][height <=? {qual}]+bestaudio/best[ext=m4a][height <=? {qual}]/best'

		ydl_opts.update({'format' : fmt, 'merge_output_format' : 'mp4'})
	
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		# remove cache
		ydl.cache.remove()
		#info = ydl.extract_info(url, download=False)
		info = ydl.download([url])

	return outfile

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--url', action='store', type=str, required=True, help="Url to download")
	parser.add_argument('-i', '--info', action='store_true', help="Extract meta info of the video")
	parser.add_argument('-a', '--audio-only', action='store_true', help="Extract audio only")
	parser.add_argument('-p', '--playlist', action='store_true', help="Url is part of a playlist")
	parser.add_argument('-q', '--quality', action='store', type=int, default=1080, help="Specify video quality (1080, 720, 480, 360)")

	args = parser.parse_args()

	url = args.url
	if args.info == True:
		info = do_extract_info(url)
		pprint.pprint(info)
	else:
		do_download(url, args.quality, args.audio_only, args.playlist)

if __name__ == "__main__":
	main()
