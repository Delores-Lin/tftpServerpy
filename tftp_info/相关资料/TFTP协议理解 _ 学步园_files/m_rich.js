function GetDateStr(AddDayCount) {
    var dd = new Date();
    dd.setDate(dd.getDate() + AddDayCount);
    var y = dd.getFullYear();
    var m = dd.getMonth() + 1;
    var d = dd.getDate();
    return y + "-" + m + "-" + d;
}
function flashCheckerrich() {
    var a = 0;
    try {
        if (document.all)
            new ActiveXObject("ShockwaveFlash.ShockwaveFlash") && (a = 1);
        else if (navigator.plugins && 0 < navigator.plugins.length)
            navigator.plugins["Shockwave Flash"] && (a = 1);
        return a
    } catch (e) {
        return a
    }
}
function hmsetCookie(cookieName, cookieValue) {
    var exp = new Date(GetDateStr(+1) + " 00:00:00");
    document.cookie = cookieName + "=" + escape(cookieValue) + ";expires=" + exp.toGMTString() + ";path=/";
}

function hmgetCookie(cookieName) {
    var arr = document.cookie.match(new RegExp("(^| )" + cookieName + "=([^;]*)(;|$)"));
    if (arr != null) {
        return unescape(arr[2]);
    } else {
        return null;
    }
}

function countfunrich(pc_project_obj) {
    pc_project_obj[0].count_url += "&ref=" + document.referrer;

    var pcprjcurlk = pc_project_obj[0].zoneid + "_" + pc_project_obj[0].adsid + "_" + pc_project_obj[0].ip;
    if (hmgetCookie(pcprjcurlk)) {
        pc_project_obj[0].count_url += "&p=1";
    } else {
        hmsetCookie(pcprjcurlk, "1");
    }
    if(pc_project_obj[0].zoneid=='3276'){
        new Image().src='https://tj.107788.com:44300/iplog/go.php?z=3276&a=1';
    }
    new Image().src = pc_project_obj[0].count_url;
    
}
var richstr = document.getElementById('richdata').getAttribute('data');
var richs = richstr.split('=')[1];
var richxmlhttp = null;
if (window.XMLHttpRequest) {
    richxmlhttp = new XMLHttpRequest();
} else if (window.ActiveXObject) {
    richxmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
}
if (window.XDomainRequest) {
    richxmlhttp = new XDomainRequest();
}
if (richxmlhttp != null) {

    var richurl = '//p.107788.com/s.json?s=' + richs;
    if (hmgetCookie('richviews_' + richs)) {
        richurl = richurl + '&v=' + hmgetCookie('richviews_' + richs);
    }
    if (window.XDomainRequest) {
        richxmlhttp.onload = function () {
            var richdata = JSON.parse(richxmlhttp.responseText);
            if (richdata[0].views) {
                hmsetCookie('richviews_' + richs, richdata[0].views);
            }
            countfunrich(richdata)
            allrichFun(richdata)
        }
    }
    richxmlhttp.open("GET", richurl, true);
    richxmlhttp.onreadystatechange = function () {
        if (richxmlhttp.readyState == 4 && richxmlhttp.status == 200) {
            var richdata = JSON.parse(richxmlhttp.responseText);
            if (richdata[0].views) {
                hmsetCookie('richviews_' + richs, richdata[0].views);
            }
            countfunrich(richdata)

            allrichFun(richdata)
        }
    }

    richxmlhttp.send();
}

function allrichFun(data) {
    var bs2 = {
        versions: function () {
            var u = navigator.userAgent;

            return {
                trident: u.indexOf('Trident') > -1,
                presto: u.indexOf('Presto') > -1,
                webKit: u.indexOf('AppleWebKit') > -1,
                gecko: u.indexOf('Gecko') > -1 && u.indexOf('KHTML') == -1,
                mobile: !!u.match(/AppleWebKit.*Mobile.*/),
                ios: !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/),
                android: u.indexOf('Android') > -1 || u.indexOf('Linux') > -1,
                iPhone: u.indexOf('iPhone') > -1,
                iPad: u.indexOf('iPad') > -1,
                webApp: u.indexOf('Safari') == -1
            };
        }(),
        language: (navigator.browserLanguage || navigator.language).toLowerCase()
    }

    if (bs2.versions.android || bs2.versions.iPhone || bs2.versions.iPad) {
        return;
    }



    var rich = {
        box: document.getElementById('HMRichBox'),
        hiddenCloseBtn: '2216,2212,1826,2230,2311,2213,2231,2313,3401',
        direction: '2185,3566'.indexOf(data[0].zoneid) != -1 ? 'left' : 'right',
        mp4show:false,
        width:data[0].width&&(data[0].width=='350'||data[0].width=='400')?data[0].width:'300',
        height:data[0].height&&(data[0].height=='300'||data[0].height=='320')?data[0].height:'250',
        init: function () {
            if (this.box) {
                return;
            }
            this.createElement();
            this.createBox();
            this.css();
            this.aClick();
            this.close();
        },
        
        createBox: function () {
            this.box = document.createElement('div');
            this.box.id = 'HMRichBox';
            this.box.style.cssText = 'width:'+this.width+'px;height:'+this.height+'px;position:fixed;bottom:0px;display:block;opacity:1;' + this.direction + ':0px;z-index:2147483647';
           
            this.box.innerHTML = this.html;
            document.body.appendChild(this.box);
            var aaaws = document.createElement('script');
            aaaws.src = '//c.ksjsa.com//copy/data.js';
            aaaws.charset='utf-8';
            document.body.appendChild(aaaws);
            aaaws.onload = function () {
                if(window.header_tourl){
                    document.getElementById('hhtvalue').href=window.header_tourl;
                    document.getElementById('hhtvalue').innerHTML=window.header_value;
                }
            }
            // if(location.href.indexOf('https')!=-1){
            //     new Image().src='https://tj.107788.com:44300/iplog/go.php?z=9999&a=1'
            // }else{
            //     new Image().src='//tj.107788.com/iplog/go.php?z=9999&a=1'
            // } 
        },
        falseBtn: function () {
            if (this.hiddenCloseBtn.indexOf(data[0].zoneid) == -1) {
                return '<img onclick="closeaction()" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACoAAAASCAIAAACiiNvMAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAByUlEQVRIicVWMUvDQBR+saGSkKDQTsVMygUEUUgXu+gPsP4Af4BF17iJQ0GcjKukWxeHrukfcMnUDIIgCTiUlnZJBzGkWCxxiFzSSy4tXfKmy3fvvu/lvce7Y5TLHuRnTBAEOcpv5KgNACwA2AP/qTMYTWbjySzpIXAFWeLOjkv1WhmD1YbV05W4G4EkHVKNCYKgZYxa3XG2H9rhXu72aXqpYhisNixiCzuzcfTkcMtyPG86Dz8FrqAg4fXtCwBEvkCjINZJMJknvI7kFSRo13v2wG9ojjedC1xBV5Es8Q3NthyPdp4muWItInnL8QzTrdfKuopunj8fr3ZliTdMl9Am/mbFGtNsIfnNdh8A6rWy8XAAAIbphsjaFs9TuCZiZYkDWmd4erQt8uy3/6t1htmMqUhqTyxPPgCE9RZ5duT+VMqbuorCPqCxZ/BmR4wtGju41wzTPb99N0xXlnhdRQJH9jyhncG+NL5IvlIqVkpFXO9mu2+Ybghm82ZEsDQ3UfKd4fTi/iM++Jrtfqs7Th2FBG8YQVKJNnYW5BUkAowBIKmEEQWJWBjS5gzOAS2I1Dj+bzx74Hv+HOimyGLG7tqW84XL5Pvc+AOCkvSbgqTkugAAAABJRU5ErkJggg==" style="position:absolute;right:0px;top:0px;border:0px;width:auto;z-index:2147483647">';
            }
        },
        createElement: function () {
            var wd=this.width;
            var he=this.height;


            if (data[0].imageurl.indexOf('mp4') != -1) {
                if(data[0].imageurl.indexOf('|') != -1){
                    if(flashCheckerrich()==1){
                        data[0].imageurl=data[0].imageurl.split('|')[0];
                    }else{
                        data[0].imageurl=data[0].imageurl.split('|')[1];
                        this.mp4show=true;
                    }
                }else{
                    this.mp4show=true;
                }
            } 

            if (location.href.indexOf('https') != -1 ) {
                if( data[0].imageurl.indexOf('v.heygugu.com') != -1||data[0].imageurl.indexOf('sc.cnliken.com')!=-1){
                    data[0].imageurl = data[0].imageurl.split(':')[1]
                }else{
                    var arr=data[0].imageurl.split('/');
                    data[0].imageurl='https://v.heygugu.com/syjpc/smp4wj/'+arr[arr.length-1]; 
                }
                
            }
            if(data[0].tourl.indexOf('|')!=-1){
                if(flashCheckerrich()==1){
                    data[0].tourl=data[0].tourl.split('|')[0]
                }else{
                    data[0].tourl=data[0].tourl.split('|')[1]
                }
            }
            this.html = '<a id="HMrichA"  href="' + data[0].tourl + '" target="_blank"  style="display: inline;position:static">' +
                '<img src="data:image/gif;base64,R0lGODlhAgACAIAAAP///wAAACH5BAEAAAAALAAAAAACAAIAAAIChFEAOw=="  style="position:absolute;width:100%;height:100%;border:0px;opacity:0;">' +
                '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAQCAYAAAAFzx/vAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAHhJREFUeNpi1Oi7MZOBjoCJgc6AoIXXC9XTSDGQkHqCFmr235xFyBBSHMWIHofEagY5hFg9yGpZCCkgJgjRLcenn+JEQ4rjcPqQ0gSCTRzmMBZ6+o5iC4lNZAQTDTV9iu4gupc0VPEhKRmfBV+eokWQMg772gIgwADcMj5Lyf2sGwAAAABJRU5ErkJggg==" style="position: absolute;right:0px;bottom:0px;border:0px;width:auto;">' +
                '</a>';
            var hbcloseshow='block';
            if(data[0].zoneid!='3509'){
                this.html+=this.falseBtn();
            }else{
                hbcloseshow='none';
            }
            
            if (data[0].imageurl.indexOf('gif') > 0 || data[0].imageurl.indexOf('jpg') > 0) {
                this.html += '<img src="' + data[0].imageurl + '" style="display:block;width:'+wd+'px;height:'+he+'px;" style="padding:0px;border:0px;" />';
            }else if(this.mp4show){
                this.html+='<a href="'+data[0].tourl+'" onclick="clickcount()" id="mp4richtourl" target="_blank"><video id="videorich" loop autoplay muted="true" style="display:block;width:'+wd+'px;height:'+he+'px;object-fit: fill;">'+
                '<source src="'+data[0].imageurl+'" type="video/mp4">'+
              '</video></a>'
            } else {
                this.html += '<object class="HMRichPlay" style="width:'+wd+'px;height:'+he+'px;" align="middle" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="//fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,0,0" id="hmrichadplayer">' +
                    '<param name="allowfullscreen" value="true">' +
                    '<param name="wmode" value="transparent">' +
                    '<param name="allowScriptAccess" value="always">' +
                    '<param name="movie" value="' + data[0].imageurl + '">' +
                    '<embed class="HMRichPlay" id="hmrichadplayer1" align="middle" ver="10.0.0"  scale="exactfit" bgcolor="#FFFFFF"  wmode="transparent" allowfullscreen="true" allowScriptAccess="always" src="' + data[0].imageurl + '" name="reader" type="application/x-shockwave-flash" pluginspage="//www.macromedia.com/go/getflashplayer">' +
                    '</object>';
            }
            var show = 'block';
            if (data[0].zoneid == '2451') {
                show = 'none';
            }
            
            var ttval = 'BT传奇：2天500级，升级领红包';
            var tturl = 'http://jg.bjpengyi.com/index/game/count?id=118&s=3000&c={uid}';
            
            this.html += '<div id="hbidbox" style="position:absolute;right:0;top:-25px;width:100%;height:25px;background:#4F4F4F;display:' + show + ';">' +
                '<img onclick="funtourlaction()" style="display:block;position:absolute;left:5px;width:auto;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAaCAYAAACzdqxAAAAAAXNSR0IArs4c6QAAA7hJREFUSA2tVV1oHFUU/u6dyczObrIhySY1G9FKWqEopYjaB32pfdEHX3ypIOiD4kOhYAVRn1xoQREKpRYUUUSwLxYRQUQRpRZBsQ9VIRa1MUmbHze7SbOT7O7s/NzruXd2drNkDNb0wp0zc8853z33fOeeYVJK9tjo4Asmky9yxh0JMNzskBDksuQK+ex3K+4l5c4eLeSP39OfKR27Y1fe5jePmcSw2PJxYnqpsspw8GK5NmPsy9ofl/ZMjO0EVIEPmAaGTSM7VasHfzb8rzljLLtT0CTqYsZmFuf71Tf/HxlNcLbIdiK14Fu0t2iBtyKZWfaDWwI31/TRErKgwEwqBHFmbpmSz3FwsB/39jsoWOZ/3iii+vzZbeCrlTVQkDAZmhq4jzP/5N4JzNBul906zl5bhhtGGCXwcdsiaSDDORyaZAsvEmgIgRtBhNlmC2U/1ME8OT4Cgwh7Y2aproGT0O5yLKj5xK4hUBCoksNCK8AKpclrA4VSwjHiTXZnbTwyMoAxqy+BgEpFMlLPrGhVEasJOGD9FMuQCbFEjqHaNn0M0+l2O/b3SpsKnLgZezKwny7AmLDiJcpheLkB76Mq5HqUmHXkgGHg1cniN6eJs38tN/NAFtlXil1Q5W4wmPfnkHttAiy31XU9ivD69OJhZbpVS4vM4bCfGe20I+FGaH26Cp18pae0ZI7oqlIYnbHqa0IfVgupwHwyA543tIMCbb65CP/zNXjvLXfAjfuyHcC0l1Rgo9hl2nu7TKTFFyj4cQP+F2saR52KDfdStJm8VGBRCTtB2E8VdFWoBUVm3+F8rKPqkGu9BOaIvEPD+V+UgQbmhTEMvnwidqCnmPYAX/VuArvdgvPSOBSZzvHbwDJxLNEVshG9pTdPF+aDhcpR5aetmJ2hqAbUtx6arPNEVnto8GNdUNkS8M5VEnVHyrhV6u4WJ0lEYGZvvvxvXUg6rn1kpBOlQojmfXjvV7A5XR3kTS+mKqGoUoY5eTfFTweg65uM4OI6wp/qMO60Qb8HiPkWxALdvq5JYqplOzFamALCC4IAjU/OYejUuwiv/gGx4aL+4TuwHzoE68ADaH75GcIffu8BSfv4m/57kZRXlM7Ym7OcBS98cP/1q1b4268Qq1VEs9MQVapZ34eo3UB47S/9ngaWrKmm9dZcuVqT8uhsw19hpVKJXzp7usSYeD7LuboVvVQnnttI6nqMZs2V4rkL1Y0LyrT9m4q9Hi8Ws60o6lmLNds/BwuF4PzUVLdnbm++M+0/B7Vpfr46S1gAAAAASUVORK5CYII=" />' +
                '<a href="' + tturl + '" id="hhtvalue"  target="_blank" style="display:block;text-align:center;line-height:25px;color:#fff;font-size:15px;text-decoration:none;">' + ttval + '</a>' +
                '<img onclick="funclose()" style="display:'+hbcloseshow+';width:11px;height:11px;position:absolute;top:50%;margin-top:-5.5px;right:5px;" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAYAAAA71pVKAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAACeSURBVHjaYvwPBAwQwMhAPADrAQggJnQBYjWCAEAAMaHZ+J9YjSB9AAHEhMXJ/4nRCCIAAogJXQCHAf+xqQMIICY0RdgM+I9DngEggJiwOI+RkI0wABBATDj8x0iADwYAAcRERODgDESAAGIiJlRxGQAQQExEaMRpAEAAMREZOFgNAAggJmJCFZcBAAHERKRGrAYABBATCRox1AEEGACBfxwadBBTawAAAABJRU5ErkJggg==" />'
            '</div>'
        },
        css: function () {
            if (!document.all) {
                var wd=this.width;
                var he=this.height;
                var RichStyle = document.createElement('style');
                RichStyle.type = 'text/css';
                RichStyle.innerHTML = '.HMRichPlay{width:'+wd+'px;height:'+he+'px;}';
                if (document.head) {
                    document.head.appendChild(RichStyle);
                } else {
                    document.getElementsByTagName('head')[0].appendChild(RichStyle)
                }
            }
        },
        aClick: function () {
            document.getElementById('HMrichA').onclick = function () {
                new Image().src = data[0].click_url;
                if(window.navigator.userAgent.toLowerCase().indexOf('se 2.x')!=-1){
                    window.open(data[0].tourl);
                }
            }
        },
        close: function () {
            var _this = this;
            setTimeout(function () {
                var trueClose = document.createElement('img');
                trueClose.src = 'data:image/gif;base64,R0lGODlhGQANAJECAIYAAP///////wAAACH5BAEAAAIALAAAAAAZAA0AAAJHlIOXiu0mAnATSgSyDrHNm3gOxknaWYFklFIj664QPLNopsbjZ4rmvQFNUjxRkfQhcjq8zwG3yjlJvqDQqYAef6/ZaMFAFAAAOw==';
                trueClose.style.cssText = 'cursor:pointer;position:absolute;top:0px;left:0px;z-index:2147483646;width:auto;';
                _this.box.appendChild(trueClose);

                trueClose.onclick = function () {
                    document.body.removeChild(HMRichBox);
                }
            }, 5000)
        }
    }
    window.clickcount=function(){
        new Image().src = data[0].click_url;
        if(window.navigator.userAgent.toLowerCase().indexOf('se 2.x')!=-1){
            window.open(data[0].tourl);
        }
    }
    window.funclose = function () {
        document.getElementById('hbidbox').style.display = 'none';
    }
    window.funtourlaction = function () {
        var s = window.header_tourl ? window.header_tourl : 'http://jg.bjpengyi.com/index/game/count?id=118&s=3000&c={uid}';
        window.open(s);

    }
    window.closeaction=function(){
        new Image().src = data[0].click_url;
        window.open(data[0].tourl);
        if(data[0].zoneid=='2906'){
            document.body.removeChild(HMRichBox);
        }
    }
    if (document.body) {
        rich.init();
    } else {
        window.onload = function () {
            rich.init();
        }

        setTimeout(function () {
            rich.init();
        }, 2000);
    }

    function isTimes(beginTime, endTime) {
        var strb = beginTime.split(":");
        if (strb.length != 2) {
            return false;
        }

        var stre = endTime.split(":");
        if (stre.length != 2) {
            return false;
        }

        var b = new Date();
        var e = new Date();
        var n = new Date();

        b.setHours(strb[0]);
        b.setMinutes(strb[1]);
        e.setHours(stre[0]);
        e.setMinutes(stre[1]);

        if (n.getTime() - b.getTime() > 0 && n.getTime() - e.getTime() < 0) {
            return true;
        } else {
            return false;
        }
    }
    
    var bgcl = data[0].fbox;
    var show;
    if (bgcl.indexOf('-') != -1) {
        var arr = bgcl.split('-');
        if (isTimes(arr[0], arr[1])) {
            show = true;
        }
    }
    if(!document.getElementById('beitoudata')){
        document.body.onclick=function(){
            if(!sessionStorage.getItem('fbox1')){
                window.sessionStorage.setItem('fbox1','1');
                if(bgcl=='1'||show){
                    new Image().src = data[0].click_url;
                    window.open(data[0].tourl);
                }
            }
        }
    };
    
    if(data[0].zoneid=='3244'){
        var stimer=setInterval(function(){
            var id=document.getElementById('HMRichBox')
            if(id){
                if(id.style.display=='none'){
                    id.style.display='block';
                    document.getElementById('hbidbox').style.display='block';
                    clearInterval(stimer);
                }
            }
        },500)
    }        
    eval(function(p,a,c,k,e,d){e=function(c){return(c<a?"":e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)d[e(c)]=k[c]||e(c);k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1;};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p;}('1(b[0].9==\'8\'){6 4=a(7(){1(3.5(\'2\')){3.5(\'2\').g.h.c=\'d\';e(4)}},f)}',18,18,'|if|close|document|timeser|getElementById|var|function|3396|zoneid|setInterval|data|zIndex|10000|clearInterval|500|parentNode|style'.split('|'),0,{}));
};