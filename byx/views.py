import re
import json
import logging
from byx import models
from datetime import datetime
# from django.db import connection
from django.shortcuts import render, HttpResponse

logger = logging.getLogger('django')
custom_logger = logging.getLogger('project.custom')

type_dic = {
    0: "沪深A股",
    1: "大连商品期货",
    2: "上海商品期货",
    3: "郑州商品期货",
    4: "中金所期货",
    10: "用户首次上行",
    11: "固定内容(如宝盈线)",
    12: "期货品种",
    98: "首次上行",
    99: "无效上行"
}

ret_msg = "代码:{code}<br>名称:{name}<br>涨幅:{gains}<br>收盘:{closing}<br>成交量:{turnover}<br>总金额:{totalMoney}<br>" \
          "{today}压力:{pressure}<br>{today}支撑:{support}<br>{tomorrow}压力:{tPressure}<br>{tomorrow}支撑:{tSupport}<br>"


def index(request):
    data_count(10)  # 用户首次上行
    logger.debug(request)
    custom_logger.info(request)
    for key in request.COOKIES:
        print(key, request.COOKIES.get(key, "xxxxx"))
    return render(request,
                  "ai.html", )


def query(request):
    para = request.GET.get("para")  # 获取用户输入的内容
    logger.debug("%s-%s" % (para, request))
    custom_logger.info("%s-%s" % (para, request))
    ret_default = {"messages":
                       [{"t": "0",
                         "msg": "您的关键词不太详细哦，再告诉小美一次吧!"}
                        ]
                   }
    js_msg = "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>"
    hy_msg = "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">您还想查询{name}的其它合约吗?(Y)</a>"
    data_type = None
    last_msg = para  # 用户最后一次交互上行内容
    session_last_msg = request.session.get("last_msg", "help")
    print("+++++++", last_msg, session_last_msg)
    # 打开首页提示信息
    if para == "help" and session_last_msg == "help":
        para = request.session.get("last_msg", "help")
        print("===========", para)
        ret = {"messages":
                   [{"t": "0",
                     "msg": "我是贴心为你服务的客服小美。"
                     },
                    {"t": "1",
                     "msg": "这是否是您需要的问题:<br>"
                            "<a href=\"javascript:void(0);\" onclick=\"set_para(\'宝盈线\');\">宝盈线是什么？<br>"
                            "</a><a href=\"javascript:void(0);\" onclick=\"set_para(\'铜主力\');\">"
                            "<font color=#ff1400>铜主力合约</font>的明日压力位和支撑位？</a><br>"
                            "<a href=\"javascript:void(0);\" onclick=\"set_para(\'中国中车\');\">"
                            "<font color=#ff1400>中国中车</font>的明日压力位和支撑位？</a><br>"
                     },
                    {"t": "0",
                     "msg": "输入关键字查询宝盈线（例如：CU、铜、中国中车、601766）"
                     }
                    ]
               }
        data_type = 10
    elif para == "宝盈线":
        data_type = 11  # 固定内容回复
        ret = {"messages":
                   [{"t": "0",
                     "msg": "宝盈线是由每日支撑位和压力位相连接构成的策略图形。根据趋势信号预判每日支撑位和压力位，为您提供合理的投资建议。"
                     }
                    ]
               }
    else:  # 需要查库的操作
        if para.isdigit():  # 全数字为股票代码
            if len(para) == 6:
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_stock(para)}
                            ]
                       }
            else:
                ret = {"messages":
                           [{"t": "0", "msg": "错误的股票代码!"}]
                       }
                last_msg = "help"
        else:  # 非数字--> 查询股票或期货
            # 先匹配期货信息
            if len(para) > 2 and para.endswith("主力"):  # 查询主力合约
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)},
                            {"t": "1",
                             "msg": hy_msg.format(name=para[0:-2])}
                            ]
                       }
            elif len(para) > 2 and para.endswith("指数"):  # 查询主力指数
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)}
                            ]
                       }
            elif re.match(r'^[A-Za-z]+\d+$', para):  # 以字母开头以数字结尾的字符串, 为期货信息, 如果cu1711
                code = re.search(r'^[A-Za-z]+', para)
                obj = models.Futures.objects.filter(code=code.group()).first()
                if obj:
                    ret = {"messages":
                               [{"t": "0",
                                 "msg": query_futures_code(para)},
                                {"t": "1",
                                 "msg": hy_msg.format(name=obj.name)}
                                ]
                           }
                    data_type = 12
                else:
                    data_type = 99
                    last_msg = "help"
                    ret = ret_default
            elif re.match(r'^.+\d+$', para):  # 以中文开头以数字结尾的字符串, 为期货信息, 如果铜1711
                new_para = re.search(r'\d+', para).group()
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)},
                            {"t": "1",
                             "msg": hy_msg.format(name=para.replace(new_para, ""))}
                            ]
                       }
            else:
                msg = ""
                if re.match(r'[A-Za-z]+', para):  # 匹配到纯字母, 获取期货信息
                    data_all = models.Data.objects.filter(code__istartswith=para)
                    if data_all:
                        for data in data_all:
                            msg += js_msg.format(name=data.name)
                            data_type = data.dataType
                        ret = {"messages":
                                   [{"t": "1",
                                     "msg": msg}
                                    ]
                               }
                    else:
                        last_msg = "help"
                        ret = ret_default
                        data_type = 99
                else:  # 先获取期货品种信息
                    if para.endswith("更多"):
                        new_para = para.replace("更多", "")
                    else:
                        new_para = para
                    futures = models.Futures.objects.filter(veriety__startswith=new_para)

                    if futures.count() >= 24:
                        ret = ret_default
                        last_msg = "help"
                        data_type = 99
                    elif futures.count() >= 1:
                        last_msg = new_para
                        data_type = 12
                        num = 0
                        for future in futures:
                            data_type = 12
                            num += 1
                            if futures.count() > 15:  # 多于15条记录, 分次返回
                                if para.endswith("更多"):
                                    if num >= 12:
                                        msg += js_msg.format(name=future.name)
                                elif num < 12:
                                    msg += js_msg.format(name=future.name)
                                else:
                                    more_info = para + "更多"
                                    msg += js_msg.format(name=more_info)
                                    break
                            else:  # 小于等于15条记录, 一次返回所有结果
                                msg += js_msg.format(name=future.name)
                        ret = {"messages":
                                   [{"t": "1",
                                     "msg": msg}
                                    ]
                               }
                        data_count(data_type)
                    else:  # 不是期货品种关键字
                        product = models.Products.objects.filter(pname=para).first()  # 获取期货产品关键字
                        if product:
                            query_name = product.fname
                        else:
                            query_name = para
                        data_all = models.Data.objects.filter(name__istartswith=query_name)

                        if data_all:
                            counts = data_all.count()
                            num = 0
                            t = "1"
                            for data in data_all:
                                num += 1
                                if data.dataType == 0:  # 查询结果为股票
                                    data_type = 0
                                    last_msg = query_name
                                    dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing,
                                               turnover=data.turnover,
                                               totalMoney=data.totalMoney, pressure=data.pressure, support=data.support,
                                               tPressure=data.tPressure,
                                               tSupport=data.tSupport, today=date2str(data.dataDate),
                                               tomorrow=date2str(data.nextDate), dataType=data.dataType)
                                    msg = ret_msg.format(**dic)
                                    t = "0"
                                    break
                                # if re.match(r'.*\d+\Z', data.name):
                                else:  # 查询结果为期货信息(datatype>=1)
                                    if counts > 15:  # 结果大于24条, 返回帮助信息
                                        t = "0"
                                        msg = "您的关键词不太详细哦，再告诉小美一次吧!"
                                        data_type = 99
                                        last_msg = "help"
                                        break
                                    if counts <= 15:  # 小于15条, 一次返回所有
                                        data_type = data.dataType
                                        t = "1"
                                        msg += js_msg.format(name=data.name)
                            ret = {"messages":
                                       [{"t": t,
                                         "msg": msg}
                                        ]
                                   }
                        else:
                            ret = ret_default
                            data_type = 99
    logger.debug(ret)
    custom_logger.info(ret)
    if data_type:
        data_count(data_type)
    request.session['last_msg'] = last_msg

    return HttpResponse("%s" % json.dumps(ret))


def query_stock(para):
    """
    股票查询
    :param para: 股票代码或者股票名称
    :return: 查询结果·
    """
    data_type = 99
    msg = "您的关键词不太详细哦，再告诉小美一次吧!"
    try:
        data = models.Data.objects.filter(code=para).first()
        if data:
            dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                       totalMoney=data.totalMoney, pressure=data.pressure, support=data.support,
                       tPressure=data.tPressure, tSupport=data.tSupport, today=date2str(data.dataDate),
                       tomorrow=date2str(data.nextDate))
            msg = ret_msg.format(**dic)
            data_type = data.dataType
    except Exception as e:
        logger.error(e)
    finally:
        data_count(data_type)
        return msg


def query_futures_name(para):
    """
    期货主力合约及指数(名称)查询
    :param para: 
    :return: 
    """
    data_type = 99
    msg = "您的关键词不太详细哦，再告诉小美一次吧!"
    try:
        data = models.Data.objects.filter(name__iendswith=para).first()
        if data:
            dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                       totalMoney=data.totalMoney, pressure=data.pressure, support=data.support,
                       tPressure=data.tPressure, tSupport=data.tSupport, today=date2str(data.dataDate),
                       tomorrow=date2str(data.nextDate))
            msg = ret_msg.format(**dic)
            data_type = data.dataType
    except Exception as e:
        logger.error(e)
    finally:
        data_count(data_type)
        return msg


def query_futures_code(para):
    """
    期货主力合约及指数(代码)查询
    :param para: 
    :return: 
    """
    data_type = 99
    msg = "您的关键词不太详细哦，再告诉小美一次吧!"
    try:
        data = models.Data.objects.filter(code__icontains=para).first()
        if data:
            dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                       totalMoney=data.totalMoney, pressure=data.pressure, support=data.support,
                       tPressure=data.tPressure, tSupport=data.tSupport, today=date2str(data.dataDate),
                       tomorrow=date2str(data.nextDate))
            msg = ret_msg.format(**dic)
            data_type = data.dataType
    except Exception as e:
        logger.error(e)
    finally:
        data_count(data_type)
        return msg


def date2str(dt):
    return "{}年{}月{}日".format(dt.year, dt.month, dt.day)


def data_count(data_type):
    """
    数据统计
    :param data_type: 0:股票, 1-4:期货, 10: 用户首次上行, 11: 固定内容（如：宝盈线）, 12:期货品种, 99: 无效上行
    :return: 
    """
    current_date = datetime.now().date()
    try:
        obj = models.Tj.objects.filter(type=data_type, date=current_date).first()
        if obj:
            obj.counts += 1
            models.Tj.objects.filter(type=data_type, date=current_date).update(counts=obj.counts,
                                                                               name=type_dic.get(data_type, "无效上行"))
        else:
            models.Tj.objects.create(type=data_type, date=current_date, counts=1, name=type_dic.get(data_type, "无效上行"))
    except Exception as e:
        logger.error(e)
