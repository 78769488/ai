import re
import json
import logging
from byx import models
from datetime import datetime
from django.db import connection
from django.shortcuts import render, HttpResponse


logger = logging.getLogger('django')
custom_logger = logging.getLogger('project.custom')

type_dic = {
    0: "沪深A股",
    1: "大连商品期货",
    2: "上海商品期货",
    3: "郑州商品期货",
    4: "中金所期货",
    10: "会话次数",
    11: "固定内容(如宝盈线)",
    12: "期货品种",
    99: "无效上行"
}

ret_msg = "代码: {code}<br>名称: {name}<br>涨幅: {gains}<br>收盘: {closing}<br>成交量: {turnover}<br>总金额: {totalMoney}<br>{" \
          "today}压力: {pressure}<br>{today}支撑: {support}<br>{tomorrow}压力: {tPressure}<br>{tomorrow}支撑: {tSupport}<br>"


def index(request):
    data_count(10)  # 用户首次上行
    logger.debug("-" * 100)
    for k, v in request.META.items():
        logger.debug("%s: %s" % (k, v))
    logger.debug(request)
    custom_logger.info("用户打开会话页面：%s" % request)
    logger.debug("-" * 100)
    return render(request, "ai.html", )


def query(request):
    para = request.GET.get("para")  # 获取用户输入的内容
    logger.debug("用户上行内容：%s" % para)
    custom_log_msg = ""
    custom_log_msg += '"%s"' % para
    custom_log_msg += ","
    # custom_logger.info("%s" % para)
    para = para.strip().upper()
    ret_default = {
        "messages":
            [{"t": "0",
              "msg": "您的关键词不太详细哦，再告诉小美一次吧!"}
             ]
    }
    js_msg = "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\"><font color=#3366cc>{name}</font></a><br>"
    hy_msg = "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\"><font color=#3366cc>您还想查询{name}的其它合约吗?(Y)</font></a>"
    data_type = None
    flag = True
    session_last_msg = request.session.get("last_msg", None)
    if session_last_msg and session_last_msg != "help":
        last_msg = session_last_msg
    else:
        last_msg = para  # 用户最后一次交互上行内容
    logger.debug("session_last_msg===%s" % session_last_msg)
    # 打开首页提示信息
    if para == "HELP":
        logging.debug(para)
        # if last_msg == "help":
        ret = {
            "messages":
                [{"t": "0",
                  "msg": "我是贴心为你服务的客服小美。"
                  },
                 {"t": "1",
                  "msg": "以下是否为您需要的问题：<br>"
                         "<a href=\"javascript:void(0);\" onclick=\"set_para(\'宝盈线\');\">"
                         "<font color=#3366cc>宝盈线是什么？</font></a><br>"
                         "<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜主力\');\">"
                         "<font color=#3366cc>铜主力合约的明日压力位和支撑位？</font></a><br>"
                         "<a href=\"javascript:void(0);\" onclick=\"set_para(\'中国中车\');\">"
                         "<font color=#3366cc>中国中车的明日压力位和支撑位？</font></a><br>"
                         "点击上方蓝色问题或者输入关键字查询（例如：宝盈线、铜主力、美尔雅、600107）"
                  },
                 ]
        }

    elif para == "宝盈线":
        logging.debug(para)
        data_type = 11  # 固定内容回复
        ret = {"messages":
                   [{"t": "0",
                     "msg": "宝盈线是由每日支撑位和压力位相连接构成的策略图形。根据趋势信号预判每日支撑位和压力位，为您提供合理的投资建议。"
                     }
                    ]
               }
    else:  # 需要查库的操作
        if para.isdigit():
            if len(para) == 6:  # 全数字为股票代码
                logging.debug(para)
                ret = {
                    "messages":
                        [{"t": "0",
                          "msg": query_stock_code(para)}
                         ]
                }
            else:
                logging.debug(para)
                ret = {
                    "messages":
                        [{"t": "0", "msg": "错误的股票代码!"}]
                }
                flag = False
        else:  # 非数字--> 查询股票或期货
            # 先匹配期货信息
            if len(para) > 2 and para.endswith("主力"):  # 查询主力合约
                logging.debug(para)
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)},
                            {"t": "1",
                             "msg": hy_msg.format(name=para[0:-2])}
                            ]
                       }
            elif len(para) > 2 and para.endswith("指数"):  # 查询主力指数
                logging.debug(para)
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)}
                            ]
                       }
            elif re.match(r'^[A-Za-z]+\d+$', para):  # 以字母开头以数字结尾的字符串, 为期货信息, 如果cu1711
                logging.debug(para)
                code = re.search(r'^[A-Za-z]+', para)
                obj = models.Futures.objects.filter(code=code.group()).first()
                if obj:
                    logging.debug(para)
                    ret = {
                        "messages":
                            [{"t": "0",
                              "msg": query_futures_code(para)},
                             {"t": "1",
                              "msg": hy_msg.format(name=obj.name)}
                             ]
                    }
                    data_type = 12
                if not obj:
                    obj = models.Futures.objects.filter(name=code.group()).first()
                    if obj:
                        logging.debug(para)
                        ret = {
                            "messages":
                                [{"t": "0",
                                  "msg": query_futures_name(para)},
                                 {"t": "1",
                                  "msg": hy_msg.format(name=obj.name)}
                                 ]
                        }
                        data_type = 12
                else:
                    logging.debug(para)
                    data_type = 99
                    flag = False
                    ret = ret_default
            elif re.match(r'^.+\d+$', para):  # 以中文开头以数字结尾的字符串, 为期货信息, 如果铜1711
                logging.debug(para)
                new_para = re.search(r'\d+', para).group()
                ret = {
                    "messages":
                        [{"t": "0",
                          "msg": query_futures_name(para)},
                         {"t": "1",
                          "msg": hy_msg.format(name=para.replace(new_para, ""))}
                         ]
                       }
            else:
                msg = ""
                """
                if re.match(r'[A-Za-z]+', para):  # 匹配到纯字母, 获取期货信息
                    logging.debug(para)
                    data_all = models.Data.objects.filter(code__istartswith=para)
                    if data_all:
                        logging.debug(data_all)
                        for data in data_all:
                            msg += js_msg.format(name=data.name)
                            data_type = data.dataType
                        logging.debug(msg)
                        ret = {"messages":
                                   [{"t": "1",
                                     "msg": msg}
                                    ]
                               }
                    else:
                        logging.debug(data_all)
                        ret = ret_default
                        data_type = 99
                        flag = False
                """
                # 先获取期货品种分类信息
                logging.debug(para)
                if para.endswith("更多"):
                    para = para.replace("更多", "")

                futures = models.Futures.objects.filter(veriety=para)

                if futures.count() >= 1:
                    logging.debug(futures)
                    if futures.count() >= 23:
                        ret = ret_default
                        data_type = 99
                        flag = False
                    else:
                        last_msg = para
                        data_type = 12
                        num = 0
                        for future in futures:
                            data_type = 12
                            num += 1
                            if futures.count() > 15:  # 多于15且少于23条记录, 分次返回, 首次返回11条
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
                        ret = {
                            "messages":
                                [{"t": "1", "msg": msg}]
                        }
                        data_count(data_type)
                else:  # 不是期货品种分类
                    logging.debug(para)
                    # 判断是否模糊匹配关键字
                    product = models.Products.objects.filter(pname=para).first()  # 获取期货产品关键字
                    if product:
                        para = product.fname
                        data_all = models.Data.objects.filter(name__istartswith=para, dataType__gte=1)
                    else:
                        # 判断是否期货名称
                        name = models.Futures.objects.filter(name=para).first()
                        if name:
                            data_all = models.Data.objects.filter(name__istartswith=para, dataType__gte=1)
                        else:
                            # 判断是否期货代码
                            code = models.Futures.objects.filter(code=para).first()
                            if code:
                                data_all = models.Data.objects.filter(code__istartswith=para, dataType__gte=1)
                            else:
                                # 模糊匹配期货名称
                                print("模糊匹配期货名称")
                                data_all = models.Data.objects.filter(name__istartswith=para, dataType__gte=1)
                                if not data_all:
                                    print("模糊匹配期货代码")
                                    # 模糊匹配期货代码
                                    data_all = models.Data.objects.filter(code__istartswith=para, dataType__gte=1)
                                    if not data_all:
                                        # 模糊匹配股票名称
                                        print("模糊匹配股票名称")
                                        data_all = models.Data.objects.filter(name__istartswith=para, dataType=0)
                                        if not data_all:
                                            # 模糊匹配股票代码
                                            print("模糊匹配股票代码h")
                                            data_all = models.Data.objects.filter(code__istartswith=para,
                                                                                  dataType__gte=0)
                                            # if len(para) >= 3:
                                            #     data_all = models.Data.objects.filter(name__istartswith=para, dataType=0)
                                            # else:
                                            #     data_all = models.Data.objects.filter(name__istartswith=para, dataType__gte=1)
                    if data_all:
                        logging.debug(data_all)
                        counts = data_all.count()
                        num = 0
                        t = "1"
                        for data in data_all:
                            num += 1
                            if data.dataType == 0:  # 查询结果为股票
                                data_type = 0
                                last_msg = para
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
                                logging.debug("查询结果为期货信息")
                                data_type = data.dataType
                                if counts == 1:
                                    dic = dict(code=data.code, name=data.name, gains=data.gains,
                                               closing=data.closing, turnover=data.turnover,
                                               totalMoney=data.totalMoney, pressure=data.pressure,
                                               support=data.support, tPressure=data.tPressure,
                                               tSupport=data.tSupport, today=date2str(data.dataDate),
                                               tomorrow=date2str(data.nextDate), dataType=data.dataType)
                                    msg = ret_msg.format(**dic)
                                    t = "0"
                                    break
                                if counts > 20:  # 结果大于20条, 返回帮助信息
                                    t = "0"
                                    msg = "您的关键词不太详细哦，再告诉小美一次吧!"
                                    data_type = 99
                                    flag = False
                                    break
                                if counts <= 20:  # 小于20条, 一次返回所有
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
    # custom_logger.info("返回消息内容：%s" % ret)
    write_csv(custom_log_msg, ret)
    if data_type:
        data_count(data_type)
    if flag:
        last_msg = para
    request.session['last_msg'] = last_msg
    logger.debug("session_last_msg===%s" % last_msg)

    return HttpResponse("%s" % json.dumps(ret))


def query_stock_code(para):
    """
    股票查询
    :param para: 股票代码
    :return: 查询结果·
    """
    data_type = 99
    msg = "您的关键词不太详细哦，再告诉小美一次吧!"
    try:
        data = models.Data.objects.filter(code=para).first()
        logger.debug("股票查询：%s" % connection.queries)
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
        logger.debug("期货主力合约及指数(名称)查询：%s" % connection.queries)
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
        logger.debug("期货主力合约及指数(代码)查询：%s" % connection.queries)
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


def write_csv(custom_log_msg, res):
    no_ask = "您的关键词不太详细哦，再告诉小美一次吧!"
    log_msg = ''
    try:
        messages = res.get("messages")
        for message in messages:
            t = message.get("t")
            msg = """%s""" % message.get("msg")
            if t == "0":
                msg_formatter = msg.replace("<br>", "\n")
                log_msg += '"%s"' % msg_formatter
                log_msg += ","
                if no_ask == msg_formatter:
                    log_msg += '"是"'
            else:  # t == 1, 带链接, 设置了字体颜色
                pattern = r'<font .*?>(.*?)</font>'
                items = re.findall(pattern, msg.replace("'", ""), re.S | re.M)
                logger.debug("解析结果:%s" % items)
                log_msg += '"%s"' % "\n".join(items)
                log_msg += ","
        custom_log_msg += log_msg
    except Exception as e:
        logger.debug(e)
        log_msg = e
    finally:
        custom_logger.info(custom_log_msg)
