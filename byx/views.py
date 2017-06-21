from django.shortcuts import render, HttpResponse
from django.db import connection
# Create your views here.
# from django.contrib.auth.models import User, Group
# from rest_framework import viewsets
# from byx.serializers import UserSerializers, GroupSerializer
import re
import json
from byx import models


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     允许查看和编辑user的API endpoint
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializers
#
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     允许查看和编辑group的API endpoint
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


def index(request):
    return render(request,
                  "ai.html",)


def query(request):
    para = request.GET.get("para")  # 获取用户输入的内容
    ret_default = {"messages":
                       [{"t": "0",
                         "msg": "您的关键词不太详细哦，再告诉小美一次吧!"}
                        ]
                   }
    # 首次登录提示信息
    if para == "index":
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
    elif para == "宝盈线":
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
                           [{"t": "0", "msg": "错误的股票代码!"}
                            ]
                       }
        else:  # 非数字--> 查询股票或期货
            # 先匹配期货信息
            if len(para) > 2 and para.endswith("主力"):  # 查询主力合约
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)},
                            {"t": "1",
                             "msg": "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">您还想查询{name}的其它合约吗?(Y)</a>".format(name=para[0:-2])}
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
                name = models.Futures.objects.filter(code=code.group())
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_code(para)},
                            {"t": "1",
                             "msg": "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">您还想查询{name}的其它合约吗?(Y)</a>".format(name=name)}
                            ]
                       }
            elif re.match(r'^.+\d+$', para):  # 以中文开头以数字结尾的字符串, 为期货信息, 如果铜1711
                new_para = re.search(r'\d+', para).group()
                ret = {"messages":
                           [{"t": "0",
                             "msg": query_futures_name(para)},
                            {"t": "1",
                             "msg": "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">您还想查询{name}的其它合约吗?(Y)</a>".format(name=para.replace(new_para, ""))}
                            ]
                       }
            else:
                msg = ""
                if re.match(r'[A-Za-z]+', para):  # 匹配到纯字母, 获取期货信息
                    data_all = models.Data.objects.filter(code__istartswith=para)
                    if data_all:
                        for data in data_all:
                            msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=data.name)
                        ret = {"messages":
                                   [{"t": "1",
                                     "msg": msg}
                                    ]
                               }
                    else:
                        ret = ret_default
                else:  # 先获取期货品种信息
                    if para.endswith("更多"):
                        new_para = para.replace("更多", "")
                    else:
                        new_para = para
                    futures = models.Futures.objects.filter(veriety__startswith=new_para)

                    if futures.count() >= 24:
                        ret = ret_default
                    elif futures.count() >= 1:
                        num = 0
                        for future in futures:
                            num += 1
                            if futures.count() > 15:  # 多于15条记录, 分次返回
                                if para.endswith("更多"):
                                    if num >= 12:
                                        msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=future.name)
                                elif num < 12:
                                    msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=future.name)
                                else:
                                    more_info = para + "更多"
                                    msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=more_info)
                                    break
                            else:  # 小于等于15条记录, 一次返回所有结果
                                msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=future.name)
                        ret = {"messages":
                                   [{"t": "1",
                                     "msg": msg}
                                    ]
                               }
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
                                    rs = "代码:{code}<br>名称:{name}<br>涨幅:{gains}<br>收盘:{closing}<br>成交量:{turnover}<br>总金额:{totalMoney}<br>" \
                                          "{today}压力:{pressure}<br>{today}支撑:{support}<br>{tomorrow}压力:{tPressure}<br>{tomorrow}支撑:{tSupport}<br>"
                                    dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                                               totalMoney=data.totalMoney, pressure=data.pressure, support=data.support, tPressure=data.tPressure,
                                               tSupport=data.tSupport, today=date2str(data.dataDate), tomorrow=date2str(data.nextDate))
                                    msg = rs.format(**dic)
                                    t = "0"
                                    # ret = {"messages":
                                    #            [{"t": "0",
                                    #              "msg": rs.format(**dic)}
                                    #             ]
                                    #        }
                                    break
                                # if re.match(r'.*\d+\Z', data.name):
                                else:  # 查询结果为期货信息(datatype>=1)
                                    if counts > 15:  # 结果大于24条, 返回帮助信息
                                        t = "0"
                                        msg = "您的关键词不太详细哦，再告诉小美一次吧!"
                                        break
                                    if counts <= 15:  # 小于15条, 一次返回所有
                                        t = "1"
                                        msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=data.name)
                                    # else:  # 大于15, 小于24, 分2次返回
                                    #     if para.endswith("更多"):
                                    #         print(para, num)
                                    #         if num >= 12:
                                    #             msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=data.name)
                                    #     elif num < 12:
                                    #         msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=data.name)
                                    #     else:
                                    #         more_info = para + "更多"
                                    #         msg += "<a href=\"javascript:void(0);\" onclick=\"set_para(\'{name}\');\">{name}</a><br>".format(name=more_info)
                                    #         break
                            ret = {"messages":
                                       [{"t": t,
                                         "msg": msg}
                                        ]
                                   }
                        else:
                            ret = ret_default
    return HttpResponse("%s" % json.dumps(ret))


def query_stock(para):
    """
    股票查询
    :param para: 股票代码或者股票名称
    :return: 查询结果
    """
    data = models.Data.objects.filter(code=para).first()
    if data:
        ret = "代码:{code}<br>名称:{name}<br>涨幅:{gains}<br>收盘:{closing}<br>成交量:{turnover}<br>总金额:{totalMoney}<br>" \
              "{today}压力:{pressure}<br>{today}支撑:{support}<br>{tomorrow}压力:{tPressure}<br>{tomorrow}支撑:{tSupport}<br>"
        dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                   totalMoney=data.totalMoney, pressure=data.pressure, support=data.support, tPressure=data.tPressure,
                   tSupport=data.tSupport, today=date2str(data.dataDate), tomorrow=date2str(data.nextDate))
        return ret.format(**dic)
    else:
        return "您的关键词不太详细哦，再告诉小美一次吧!"


def query_futures_name(para):
    """
    期货主力合约及指数(名称)查询
    :param para: 
    :return: 
    """
    data = models.Data.objects.filter(name__iendswith=para).first()
    if data:
        ret = "代码:{code}<br>名称:{name}<br>涨幅:{gains}<br>收盘:{closing}<br>成交量:{turnover}<br>总金额:{totalMoney}<br>" \
              "{today}压力:{pressure}<br>{today}支撑:{support}<br>{tomorrow}压力:{tPressure}<br>{tomorrow}支撑:{tSupport}<br>"
        dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                   totalMoney=data.totalMoney, pressure=data.pressure, support=data.support, tPressure=data.tPressure,
                   tSupport=data.tSupport, today=date2str(data.dataDate), tomorrow=date2str(data.nextDate))
        return ret.format(**dic)
    else:
        return "您的关键词不太详细哦，再告诉小美一次吧!"


def query_futures_code(para):
    """
    期货主力合约及指数(代码)查询
    :param para: 
    :return: 
    """
    data = models.Data.objects.filter(code__icontains=para).first()
    if data:
        ret = "代码:{code}<br>名称:{name}<br>涨幅:{gains}<br>收盘:{closing}<br>成交量:{turnover}<br>总金额:{totalMoney}<br>" \
              "{today}压力:{pressure}<br>{today}支撑:{support}<br>{tomorrow}压力:{tPressure}<br>{tomorrow}支撑:{tSupport}<br>"
        dic = dict(code=data.code, name=data.name, gains=data.gains, closing=data.closing, turnover=data.turnover,
                   totalMoney=data.totalMoney, pressure=data.pressure, support=data.support, tPressure=data.tPressure,
                   tSupport=data.tSupport, today=date2str(data.dataDate), tomorrow=date2str(data.nextDate))
        return ret.format(**dic)
    else:
        return "您的关键词不太详细哦，再告诉小美一次吧!"


def date2str(dt):
    return "{}年{}月{}日".format(dt.year, dt.month, dt.day)


