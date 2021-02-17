var getInfo = document.querySelector("input[name=getinfo]");

getInfo.addEventListener('change', function() {
	var textEle = document.getElementById("submit-text");
	if (this.checked) {
		textEle.innerHTML = "Get Info"
	} else {
		textEle.innerHTML = "Download"
	}
});

function secondsToTime(e){
    var h = Math.floor(e / 3600).toString().padStart(2,'0'),
        m = Math.floor(e % 3600 / 60).toString().padStart(2,'0'),
        s = Math.floor(e % 60).toString().padStart(2,'0');
    
    return h + ':' + m + ':' + s;
}

function handleSubmit(evt) {

	var getinfoEle = document.querySelector("input[name=getinfo]");

	evt.preventDefault();

	if(getinfoEle.checked == true){
		getVideoInfo();
	} else {
		downloadVideo();
	}
	
}

function getVideoInfo() {
	
	var urlEle = document.querySelector("input[name=url]");

	jsonBody = JSON.stringify({ 
				url: urlEle.value
				});

	// POST request using fetch()
	fetch('/action/getinfo', { 
      
    	// Adding method type 
	    method: "POST", 
		
    	// Adding body or contents to send 
	    body: jsonBody, 

	    // Adding headers to the request 
    	headers: { 
        	"Content-type": "application/json; charset=UTF-8"
	    } 
	}) 
  
	// Converting to JSON 
	.then(function (response) {
		return response.text();
	}) 
  
	// Displaying results to console 
	.then(function (text) {

		try {
			let data = JSON.parse(text);
			console.log(data);
			
			showInfo(data);

		} catch(e) {
			console.log(e);
		}
	}); 

}

let fnGetFileNameFromContentDispostionHeader = function (header) {
	console.log(header);
    let contentDispostion = header.split(';');
    //const fileNameToken = `filename*=UTF-8''`;
    const fileNameToken = `filename=`;

    let fileName = 'video.mp4';
    for (let thisValue of contentDispostion) {
        if (thisValue.trim().indexOf(fileNameToken) === 0) {
            fileName = decodeURIComponent(thisValue.trim().replace(fileNameToken, ''));
            break;
        }
    }

    return fileName;
}

function downloadVideo() {
	
	var urlEle = document.querySelector("input[name=url]");
	var formatEle = document.querySelector("select[name=format]");
	var audioEle = document.querySelector("input[name=audio]");
	var playlistEle = document.querySelector("input[name=playlist]");
	var spinnerEle = document.querySelector("span[name=spinner]");

	jsonBody = JSON.stringify({ 
				url: urlEle.value,
				format: formatEle.value,
				audioonly: audioEle.checked,
				playlist: playlistEle.checked });

	spinnerEle.classList.add("spinner-border");
	spinnerEle.classList.add("spinner-border-sm");

	fetch('/action/download', {
		body: jsonBody,
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=utf-8'
		},
	})
    .then(async res => ({
        filename: fnGetFileNameFromContentDispostionHeader(res.headers.get('content-disposition')),
        blob: await res.blob()
    }))
    .then(resObj => {
        // It is necessary to create a new blob object with mime-type explicitly set for all browsers except Chrome, but it works for Chrome too.
        const newBlob = new Blob([resObj.blob], { type: 'application/octet-stream' });

        // MS Edge and IE don't allow using a blob object directly as link href, instead it is necessary to use msSaveOrOpenBlob
        if (window.navigator && window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveOrOpenBlob(newBlob);
        } else {
            // For other browsers: create a link pointing to the ObjectURL containing the blob.
            const objUrl = window.URL.createObjectURL(newBlob);

            let link = document.createElement('a');
            link.href = objUrl;
            link.download = resObj.filename;
            link.click();

            // For Firefox it is necessary to delay revoking the ObjectURL.
            setTimeout(() => { window.URL.revokeObjectURL(objUrl); }, 250);
        }
		
		spinnerEle.classList.remove("spinner-border");
		spinnerEle.classList.remove("spinner-border-sm");
    })
    .catch((error) => {
        console.log('DOWNLOAD ERROR:', error);
    });
}

function showInfo(data) {
	var tableEle = document.querySelector("table[name=urlinfo]");
	var fmttblEle = document.querySelector("table[name=fmtinfo]");

	var info = data['raw'];

	var duration = secondsToTime(info['duration']);

	tableEle.innerHTML = `
							<tr>
								<th>Title:</th>
								<td>${info['title']}</td>
							</tr>
							<tr>
								<th>Url:</th>
								<td>${info['webpage_url']} (${info['extractor']})</td>
							</tr>
							<tr>
								<th>Duration:</th>
								<td>${duration}</td>
							</tr>
							<tr>
								<th>Format:</th>
								<td>${info['width']} x ${info['height']} - ${info['ext']}</td>
							</tr>
							<tr>
								<th>acodec:</th>
								<td>${info['acodec']}</td>
							</tr>
							<tr>
								<th>vcodec:</th>
								<td>${info['vcodec']}</td>
							</tr>
							`;
	var fmts = info['formats'];

	innerhtml = `<thead>
					<tr>
						<th>Id</th>
						<th>Format</th>
						<th>Ext</th>
						<th>acodec</th>
						<th>vcodec</th>
						<th>width</th>
						<th>height</th>
						<th>filesize</th>
					</tr>
				</thead>
				<tbody>
				`;
	for(i=0; i < fmts.length; i++)
	{
		innerhtml += `
						<tr>
							<td>${fmts[i]['format_id']}</td>
							<td>${fmts[i]['format']}</td>
							<td>${fmts[i]['ext']}</td>
							<td>${fmts[i]['acodec']}</td>
							<td>${fmts[i]['vcodec']}</td>
							<td>${fmts[i]['width']}</td>
							<td>${fmts[i]['height']}</td>
							<td>${fmts[i]['filesize']}</td>
						</tr>
						`;
	}

	innerhtml += '</tbody>';
	fmttblEle.innerHTML = innerhtml;
}
