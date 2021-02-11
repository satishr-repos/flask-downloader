from __future__ import unicode_literals
import youtube_dl
import argparse
import pprint
import os

class MyLogger(object):
	def debug(self, msg):
		print(msg)

	def warning(self, msg):
		print(msg)

	def error(self, msg):
		print(msg)

def my_hook(d):
	if d['status'] == 'finished':
		print('Done downloading, now converting ...')

def do_extract_url(url):
    """Extract a video url."""
    params = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': '/dev/null',
        'writedescription': True,
        'writeinfojson': True,
        'writesubtitles': False,
        'subtitlesformat': 'srt/ass/vtt/best',
        'cachedir': '/tmp/',
        'noplaylist': True,  # not implemented in video2commons
    }
    info = youtube_dl.YoutubeDL(params).extract_info(url, download=False)

    assert 'formats' in info or info.get('direct'), \
        'Your url cannot be processed correctly'

    ie_key = info['extractor_key']
    title = (info.get('title') or '').strip()
    url = info.get('webpage_url') or url

    filedesc = FILEDESC_TEMPLATE % {
        'desc': _desc(url, ie_key, title, info),
        'date': _date(url, ie_key, title, info),
        'source': _source(url, ie_key, title, info),
        'uploader': _uploader(url, ie_key, title, info),
        'license': _license(url, ie_key, title, info)
    }

    return {
        'url': url,
        'extractor': ie_key,
        'filedesc': filedesc.strip(),
        'filename': sanitize(title)
    } 

def do_download(params):

	OUTPUT_PATH = os.path.join(os.getcwd(), os.path.join('..','videos'))
	outfile = os.path.join(OUTPUT_PATH, '%(title)s.%(ext)s')

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
		'outtmpl': outfile,
		'logger': MyLogger(),
		'progress_hooks': [my_hook],
	}

	list_fmts = {
		'format': 'bestaudio/best',  # choice of quality
		'extractaudio': True,        # only keep the audio
		'audioformat': "mp3",        # convert to mp3
		'noplaylist': True,          # only download single song, not playlist
		'listformats': True,         # print a list of the formats to stdout and exit
	}

	postproc = {
				'postprocessors': [{
					'key': 'FFmpegExtractAudio',
					'preferredcodec': 'mp3',
					'preferredquality': '192',
					}]
				}

	url = params['url'][0]

	if params['listfmts'] == True:
		ydl_opts.update(list_fmts)
	elif params['audioonly'] == True:
		ydl_opts.update(list_fmts)
		ydl_opts.update(postproc)
		ydl_opts.pop('listformats')
	else:
		qual = params['quality']
		fmt = f'bestvideo[ext=mp4][height<={qual}]+bestaudio/best[ext=mp4][height<={qual}]/best'
		ydl_opts.update({'format' : fmt, 'keepvideo' : True })
	
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		# remove cache
		ydl.cache.remove()
		info_dict = ydl.extract_info(url,download=False)

		if params['listinfo'] == True:
			pprint.pprint(info_dict)
		else:
			ydl.download([url])

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--url', action='append', type=str, required=True, help="Url to download")
	parser.add_argument('-i', '--info', action='store_true', help="Extract meta info of the video")
	parser.add_argument('-l', '--formats', action='store_true', help="List all supported formats")
	parser.add_argument('-a', '--audio-only', action='store_true', help="Extract audio only")
	parser.add_argument('-q', '--quality', action='store', type=int, default=1080, help="Specify video quality (1080, 720, 480, 360)")

	args = parser.parse_args()

	arg_list = {
				'url'		: args.url,
				'listinfo'	: args.info,
				'listfmts'	: args.formats,
				'audioonly'	: args.audio_only,
				'quality'	: args.quality }
				

	url = args.url
	do_download(arg_list)

if __name__ == "__main__":
	main()
