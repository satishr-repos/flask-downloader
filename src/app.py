from flask import Flask, render_template, request, redirect, url_for, jsonify, json, send_from_directory, abort,make_response
from datetime import datetime
import os
import videodl

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/action/<string:op>', methods=['post'])
def action(op):
	
	params = request.get_json()
	print(params)

	if op == 'getinfo': 	
		url = params.get('url')
		info = videodl.do_extract_info(url)

		response = app.response_class(
					response=json.dumps(info), status=200,
					mimetype="application/json")
	
		return response
	elif op == 'download':
		url = params.get('url')
		fmt = params.get('format')
		audio_only = params.get('audioonly')
		playlist = params.get('playlist')
		outfile = videodl.do_download(url, fmt, audio_only, playlist)
		head, tail = os.path.split(outfile)
		outdir = os.path.join(os.getcwd(), head)
		print(f'path:{outdir} file:{tail}')

		#res =  send_from_directory(outdir, filename=tail, as_attachment=True)
		response = make_response(send_from_directory(outdir, filename=tail, as_attachment=True), 200)
		response.headers['content-disposition'] = f"attachment; filename*=UTF-8''{tail}"
		response.headers['content-type'] = 'application/octet-stream'

		return response

	else:
		abort(404, description="Page not found!")

if __name__ == "__main__":
	app.run(debug=True,host='0.0.0.0')
