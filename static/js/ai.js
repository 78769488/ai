function set_para(search_key) {
    var ai_para = document.getElementById('ai_para');
    ai_para.value = search_key;
}
window.onload = function () {
    var arrIcon = ['/static/img/u.png', '/static/img/mfc.png'];
    var num = 0;   //控制头像改变
    var iNow = -1;  //用来累加改变左右浮动
    var btn = document.getElementById('btn');
    var text = document.getElementById('text');
    var ai_para = document.getElementById('ai_para');
    var content = document.getElementsByTagName('ul')[0];
    var img = content.getElementsByTagName('img');
    var span = content.getElementsByTagName('span');

    var date = new Date();
    var year = date.getFullYear(); //获取当前年份
    var mon = date.getMonth() + 1; //获取当前月份
    var da = date.getDate(); //获取当前日
    var day = date.getDay(); //获取当前星期几
    var h = date.getHours(); //获取小时
    var m = date.getMinutes(); //获取分钟
    if (m < 10) m = '0' + m;
    var s = date.getSeconds(); //获取秒
    var strdate = year + '年' + mon + '月' + da + '日' + ' ' + h + ':' + m;

    content.innerHTML += '<li><spanmid>' + strdate + '</spanmid></li>';

    function ai_req_time() {
        if (ai_para.value != '') {
            send_ai_req(ai_para.value);
            ai_para.value = '';
        }
    }

    window.setInterval(ai_req_time, 1000);
    // ai_para.value='!@#$%^&*';
    ai_para.value = 'help';

    function send_ai_req(para) {
        if (iNow > -1) {
            content.innerHTML += '<li><img src="' + arrIcon[0] + '"><span>' + para + '</span></li>';
        } else {
            content.innerHTML += '<li><p hidden><img src="' + arrIcon[0] + '"><span>' + para + '</span></p></li>';
        }
        iNow++;
        num = 0;
        if (num == 0) {
            img[iNow].className += 'imgright';
            span[iNow].className += 'spanright';
        } else {
            img[iNow].className += 'imgleft';
            span[iNow].className += 'spanleft';
        }
        // 获取csrftoken, 支持跨站请求
        var csrftoken = $.cookie('csrftoken');
        console.log(csrftoken);
        $.ajax({
            // url:"http://114.215.179.121:8080/ai/a.php",
            url: "/byx/query",
            data: {"para": para, "csrfmiddlewaretoken": csrftoken}, //以键/值对的形式
            async: true,
            dataType: "json",
            success: function (data) {
                $.each(data.messages, function (idx, item) {
                    content.innerHTML += '<li><img src="' + arrIcon[1] + '"><span>' + item.msg + '</span></li>';
                    //content.innerHTML +='<li><img src="'+arrIcon[1]+'"><span><a href="javascript:void(0);" onclick="set_para();">点我</a></span></li>';
                    iNow++;
                    num = 1;
                    if (num == 0) {
                        img[iNow].className += 'imgright';
                        span[iNow].className += 'spanright';
                    } else {
                        img[iNow].className += 'imgleft';
                        if (item.t == '1') {
                            span[iNow].className += 'spanleft2';
                        } else {
                            span[iNow].className += 'spanleft';
                        }
                    }
                    content.scrollTop = content.scrollHeight;
                });
                //text.placeholder=data.tips[0].msg;
            }
        });

        // 内容过多时,将滚动条放置到最底端
        content.scrollTop = content.scrollHeight + 1000;
    }

    $('.content').css('height', $(window).height() - 50);

    $('#text').on('focus', function () {
        setTimeout(function () {
            window.scrollTo(0, 1000000);
        }, 200);
    });

    $('#text').on('focus', function () {
        var agent = navigator.userAgent.toLowerCase();
        setTimeout(function () {
            if (agent.indexOf('safari') != -1 && agent.indexOf('mqqbrowser') == -1
                && agent.indexOf('coast') == -1 && agent.indexOf('android') == -1
                && agent.indexOf('linux') == -1 && agent.indexOf('firefox') == -1) {
                //safari浏览器 6
            } else {//其他浏览器
                window.scrollTo(0, 1000000);
            }
        }, 200);
    });

    $('#text').on('focus', function () {
        var agent = navigator.userAgent.toLowerCase();
        setTimeout(function () {
            if (agent.indexOf('safari') != -1 && agent.indexOf('mqqbrowser') == -1
                && agent.indexOf('coast') == -1 && agent.indexOf('android') == -1
                && agent.indexOf('linux') == -1 && agent.indexOf('firefox') == -1) {//safari浏览器
                if (scope.$txtWrap.offset().top - winobj.scrollTop() > document.body.offsetHeight / 2) { //说明软键盘遮盖页面
                    window.scrollTo(0, winobj.height() - 270);
                }
            } else {//其他浏览器
                window.scrollTo(0, 1000000);
            }
        }, 200);
    });

    $('#text').on('blur', function () {
        window.scrollTo(0, 0);
    });

    btn.onmousedown = function () {
        if (text.value == '') {
            alert('不能发送空消息');
        } else {
            ai_para.value = text.value;
            text.value = '';
        }
    }
};
