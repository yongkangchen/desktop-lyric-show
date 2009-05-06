
var AmuseServer = {
		mainWindow:null,
		AGENT_STUB_NODENAME:'commNode',
		AGENT_EVENT_NAME:'AmuseAgentEvent', 
		SERVER_EVENT_NAME:'AmuseServerEvent', 
		CLIENT_LOADLIST:	'0',
		CLIENT_LOADTRACK:	'1',
		CLIENT_LOADMP3: '2',
		CLIENT_CHECK_VERSION:'3',
		CLIENT_SEARCHTRACK: '4',
		CLIENT_SEARCHLYRIC: '5',
		CLIENT_LOADLYRIC: '6',
		CLIENT_DESKTOPLYRIC:'100',
		EXTENSION_VERSION:'2.3',
		debugMode:false,
		logfile:null,
		
		mp3Urls:null,
		init: function() {
				AmuseServer.mainWindow = window.QueryInterface(Components.interfaces.nsIInterfaceRequestor)
                  .getInterface(Components.interfaces.nsIWebNavigation)
                  .QueryInterface(Components.interfaces.nsIDocShellTreeItem)
                  .rootTreeItem
                  .QueryInterface(Components.interfaces.nsIInterfaceRequestor)
                  .getInterface(Components.interfaces.nsIDOMWindow);
       AmuseServer.mainWindow.document.addEventListener(AmuseServer.AGENT_EVENT_NAME, AmuseServer.clientEventHandler, false, true);
/*
        var prefService    = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefService);
			  var prefSvc        = prefService.getBranch(null);

			  try {
			    AmuseServer.debugMode = prefSvc.getBoolPref("amsueplayer.debug");
			  
				  var ProfD = Components.classes["@mozilla.org/file/directory_service;1"]
	                     .getService(Components.interfaces.nsIProperties)
	                     .get("ProfD", Components.interfaces.nsIFile);
					var file = Components.classes["@mozilla.org/file/local;1"]
                     .createInstance(Components.interfaces.nsILocalFile);

					if (navigator.platform.toLowerCase().indexOf('win') > -1) {
						file.initWithPath(ProfD.path + '\\extensions\\{1c25e602-e331-4b39-a8ef-f06fdc52fc61}\\amuseplayer.log');
					}
					else
					{
						file.initWithPath(ProfD.path + '/extensions/{8c8117d2-0ae2-4c31-abfb-4b10e3a394cd}/amuseplayer.log');
					}
					AmuseServer.logfile = file
				
			  } catch (ex) {}
*/
		},
		
		getSiteIndex: function(url) {
			var regGoogle = /google/;
			var regYahoo = /yahoo/;
			var regBaidu = /baidu/;
			
			return regGoogle.test(url) ? 0 : regYahoo.test(url) ? 1 : regBaidu.test(url) ? 2 : -1;
			
		},
		
		clientEventHandler: function(evt) {
			var node = evt.target;
			var cmd = evt.target.getAttribute("cmd");
		  var param = evt.target.getAttribute("param");
		  evt.preventDefault();
		 	evt = null;
		 	
		 	var flag = AmuseServer.getSiteIndex(param);
		 	encode = flag == 2 ? 'text/plain; charset=GB2312' : 'text/plain; charset=UTF-8';
		  switch(cmd)
		  {
		  	case AmuseServer.CLIENT_LOADLIST:
				  	
				  AmuseDebugOut("[clientEventHandler]receive cmd: " + cmd + " " + param);
				  AmuseServer.getData(param,
				  				 flag == 0 ? AmuseServer.loadListCallback_Google : 
				  				 flag == 1 ? AmuseServer.loadListCallback_Yahoo :
				  				 flag == 2 ? AmuseServer.loadListCallback_Baidu : null,
				  				 node, encode);
		  		break;
		  	
		  	case AmuseServer.CLIENT_LOADTRACK:
		  		AmuseDebugOut("[clientEventHandler]param: "+ param);
		  		AmuseDebugOut(param);
		  		if(flag == 0)
		  		{
		  			var data = [];
		  			data.push(['', param]);
		  			AmuseDebugOut("[clientEventHandler] CLIENT_LOADTRACK param: "+ param);
		  			AmuseServer.postEvent(node, data);
		  		}
		  		else
		  		{
			  		AmuseServer.getData(param, 
					  				 //flag == 0 ? AmuseServer.loadTrackCallback_Google : 
					  				 flag == 1 ? AmuseServer.loadTrackCallback_Yahoo :
					  				 flag == 2 ? AmuseServer.loadTrackCallback_Baidu : null,
					  				 
			  						node, encode);
		  		}
		  		break;
		  		
		   case AmuseServer.CLIENT_LOADMP3:
		   		AmuseDebugOut("[clientEventHandler]CLIENT_LOADMP3 param:"+ param);
		   		//x-user-defined
		   		//AmuseServer.getData(param, AmuseServer.getRealUrlCallback, node, "text/plain; charset=GB2312");
		   		AmuseServer.getData(param,	
				  				flag == 0 ? AmuseServer.getRealUrlCallback_Google : 
				  				flag == 1 ? AmuseServer.getRealUrlCallback_Yahoo :
				  				flag == 2 ? AmuseServer.getRealUrlCallback_Baidu : null,
				  				 
		   						node, encode);
		   		break;
		   case AmuseServer.CLIENT_CHECK_VERSION:
		   		AmuseServer.postEvent(node, AmuseServer.EXTENSION_VERSION);
		   		break;
		  
		  case AmuseServer.CLIENT_SEARCHTRACK:
		  case AmuseServer.CLIENT_SEARCHLYRIC:
					AmuseDebugOut2("[clientEventHandler]CLIENT_SEARCHTRACK param:"+ param);
					if(flag == 2) {
						var u = param.match(/@[^@]*@/)[0].split('@')[1];
						AmuseDebugOut2("==unicode== " + AmuseUtil.toHex(u));
						var gb2312 = FileIO.fromUnicode('GB2312', u);
						AmuseDebugOut2("==gb2312== " + AmuseUtil.toHex(gb2312));
						AmuseDebugOut2(AmuseUtil.encodeURIComponent_GB2312(gb2312));
						param = param.replace(/@[^@]*@/, AmuseUtil.encodeURIComponent_GB2312(gb2312));
					} 
					AmuseDebugOut2(param);
					//param = 'http://mp3.baidu.com/m?f=ms&tn=baidump3&ct=134217728&lm=0&word=%D0%ED%CE%A1'
					if(cmd == AmuseServer.CLIENT_SEARCHTRACK ) {
						AmuseServer.getData(param,	
					  				flag == 0 ? AmuseServer.searchTrackCallback_Google : 
					  				flag == 1 ? AmuseServer.searchTrackCallback_Yahoo :
					  				flag == 2 ? AmuseServer.searchTrackCallback_Baidu : null,
					  				 
			   						node, encode);
		   		}
		   		else {
						AmuseServer.getData(param,	
		  				flag == 0 ? AmuseServer.searchLyricUrlCallback_Google : 
		  				flag == 1 ? AmuseServer.searchLyricUrlCallback_Yahoo :
		  				flag == 2 ? AmuseServer.searchLyricUrlCallback_Baidu : null,
		  				 
	 						node, encode);

		   		}
		   		break;	
		   		
		   case AmuseServer.CLIENT_LOADLYRIC:
		   	var data = null;
		   	AmuseDebugOutLyrics("[clientEventHandler]CLIENT_LOADLYRIC: param:" +  param);
		   	if(flag == 0) {
		   		data = AmuseGoogle.loadSearchLyric(param, encode);
		  	} else if (flag == 2) {
			   	data = AmuseBaidu.loadSearchLyric(param, encode);
				//data=AmuseTtplayer.loadSearchLyric(param,encode);//#kanglog.com for download lyric from ttplayer.com
		  	}
		   	AmuseServer.postEvent(node, data);
		   	break;
		/*kanglog.com for desktop lyric BEGIN*/
		  case AmuseServer.CLIENT_DESKTOPLYRIC:
			AmuseUtil.XHRSync("http://localhost:8080/?setLyric="+encodeURIComponent(param));
			break;		
		  	default:
		  		alert("unkown agent cmd: " + cmd);
		  }  	
		/*kanglog.com for desktop lyric END*/
		},
		
		postEvent: function(node, data) {
			var str = encodeURIComponent(JSON.stringify(data));
			node.setAttribute("data", str);
			var e = AmuseServer.mainWindow.document.createEvent("Events");
			e.initEvent(AmuseServer.SERVER_EVENT_NAME, true, false);
			node.dispatchEvent(e);
		},
	
		getData: function(url, callback, userData, encode) {
			AmuseUtil.XHRAsync(url, encode, callback, userData);
			//callback(AmuseUtil.XHRSync(url, encode), userData);
		},
			
		loadListCallback_Baidu: function(resText, userData) {
				var data = AmuseBaidu.parseTrackList(resText, 0);
				AmuseServer.postEvent(userData, data);
				data = null;
		},
		
		loadTrackCallback_Baidu: function(resText, userData) {
			var data = AmuseBaidu.parseTrack(resText, 5, true);
			AmuseServer.postEvent(userData, data);
			data = null;
		},
		
		getRealUrlCallback_Baidu: function(resText, userData) {
			var mp3url;
			mp3url = AmuseBaidu.parseRealMp3Url(resText);
			AmuseServer.postEvent(userData, mp3url);
		},
		searchTrackCallback_Baidu: function(resText, userData) {
			var data = AmuseBaidu.parseTrack(resText, 30, true);
			
			//AmuseDebugOut2("[searchTrackCallback_Baidu]" + data);
			AmuseServer.postEvent(userData, data);
			data = null;
			
		},
	
	
		loadListCallback_Yahoo: function(resText, userData) {
				var data = AmuseYahoo.parseTrackList(resText, 0);
				AmuseServer.postEvent(userData, data);
				data = null;
		},
	
	loadTrackCallback_Yahoo: function(resText, userData) {
			var data = AmuseYahoo.parseTrack(resText, 5);
			AmuseServer.postEvent(userData, data);
			data = null;
	},
	getRealUrlCallback_Yahoo: function(resText, userData) {
		var mp3url;
		mp3url = AmuseYahoo.parseRealMp3Url(resText);
		AmuseServer.postEvent(userData, mp3url);
	},
	searchTrackCallback_Yahoo: function(resText, userData) {
			
	},
	
				
 loadListCallback_Google: function(resText, userData) {
		var data = AmuseGoogle.parseTrackList(resText, 0);
		AmuseServer.postEvent(userData, data);
		data = null;
	},
			
	loadTrackCallback_Google: function(resText, userData) {
		// nothing to do.	
	},
	getRealUrlCallback_Google: function(resText, userData)
	{
		var mp3url = AmuseGoogle.parseRealMp3Url(resText);
		AmuseServer.postEvent(userData, mp3url[0]);
	},

	searchTrackCallback_Google: function(resText, userData) {
			var data = AmuseGoogle.parseTrackList(resText, 0);
			AmuseDebugOut2("[searchTrackCallback_Google]" + data);
			AmuseServer.postEvent(userData, data);
			data = null;
	},
	
	searchLyricUrlCallback_Google: function(resText, userData) {
		
	},

	searchLyricUrlCallback_Baidu: function(resText, userData) {
	},

	searchLyricUrlCallback_Yahoo: function(resText, userData) {
	},
	
}

AmuseServer.init();
