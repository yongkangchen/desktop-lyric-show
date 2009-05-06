var AmuseTtplayer = {
	gSandbox:Components.utils.Sandbox("http://www.amuseplayer.com"),
	loadSearchLyric: function(lyricUrl, encode) {
		var params=lyricUrl.split("&")
		var word=null;
		for(var i=0;i<params.length;i++)
		{	
			var param=params[i].split("=");
			if(param[0]=="word"){
				word=param[1];
				break;
			}
		}
		lyricUrl="http://localhost:8080/?getLyric="+word;
		//alert(lyricUrl)
		//return AmuseTtplayer.parseLrcUrlList(AmuseUtil.XHRSync(lyricUrl, encode));
		var resText=AmuseUtil.XHRSync(lyricUrl);
		//alert(resText)
		return new Array({url:null, data:resText})
	},	
};
