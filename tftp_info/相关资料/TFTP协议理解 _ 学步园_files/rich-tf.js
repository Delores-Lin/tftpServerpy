(function () {
    function IsPC() {
        var userAgentInfo = navigator.userAgent;
        var Agents = ["Android", "iPhone",
            "SymbianOS", "Windows Phone",
            "iPad", "iPod"
        ];
        var flag = true;
        for (var v = 0; v < Agents.length; v++) {
            if (userAgentInfo.indexOf(Agents[v]) > 0) {
                flag = false;
                break;
            }
        }
        return flag;
    }
    var dom=document.getElementById('richid');
    var data=document.getElementById('richid').getAttribute('data');
    if(dom){
        if(IsPC()){
            
            var sp=document.createElement('script');
            sp.charset='utf-8';
            sp.src='//pc.weizhenwx.com/pc_w/m_rich.js';
            sp.id='richdata';
            sp.setAttribute('data',data);
            document.body.appendChild(sp);
        }
    }
})()