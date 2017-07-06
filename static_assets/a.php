<?php 
header('content-type:application:json;charset=utf-8');  
header('Access-Control-Allow-Origin:*');
header('Access-Control-Allow-Methods:POST');
header('Access-Control-Allow-Methods:GET');
header('Access-Control-Allow-Headers:x-requested-with,content-type');

$para=$_GET["para"];
if($para==null){$para='void';}

switch($para){
	case 'index':
		echo '{"messages": [
		  {"t":"0","msg": "我是贴心为你服务的客服小美。"},
		  {"t":"1","msg": "这是否是您需要的问题:<br><a href=\"javascript:void(0);\" onclick=\"set_para(\'宝盈线\');\">宝盈线是什么？<br></a><a href=\"javascript:void(0);\" onclick=\"set_para(\'铜主力\');\"><font color=#ff1400>铜主力合约</font>的明日压力位和支撑位？</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'中国中车\');\"><font color=#ff1400>中国中车</font>的明日压力位和支撑位？</a><br>"},
		  {"t":"0","msg":"输入关键字查询宝盈线（例如：CU、铜、中国中车、601766）"}
		 ]}';
		break;
	case '!@#$%^&*':
		echo '{"messages": [
		  {"t":"0","msg": "我是贴心为你服务的客服小美。"},
		  {"t":"1","msg": "这是否是您需要的问题:<br><a href=\"javascript:void(0);\" onclick=\"set_para(\'宝盈线\');\">宝盈线是什么？<br></a><a href=\"javascript:void(0);\" onclick=\"set_para(\'铜主力\');\"><font color=#ff1400>铜主力合约</font>的明日压力位和支撑位？</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'中国中车\');\"><font color=#ff1400>中国中车</font>的明日压力位和支撑位？</a><br>"},
		  {"t":"0","msg":"输入关键字查询宝盈线（例如：CU、铜、中国中车、601766）"}
		 ]}';
		break;
	case '宝盈线':
		echo '{
		 "messages": [
		  {"t":"0","msg": "宝盈线是由每日支撑位和压力位相连接构成的策略图形。根据趋势信号预判每日支撑位和压力位，为您提供合理的投资建议。"}
		 ]}';
		break;
	case '铜主力':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码:CUL8<br>名称:沪铜主力<br>收盘:45900<br>成交量:128784<br>总金额:295.5亿<br>2017年6月2日压力:46050<br>2017年6月2日支撑:45750<br>2017年6月3日压力:46050<br>2017年6月3日支撑:45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	case '中国中车':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码:601766<br>名称:中国中车<br>涨幅:5%<br>收盘:10.08<br>成交量:740000<br>总金额:295.5亿<br>2017年6月2日压力:10.24<br>2017年6月2日支撑:9.50<br>2017年6月3日压力:10.30<br>2017年6月3日支撑:9.60<br>"}
		 ]}';
		break;
	case '铜':
		echo '{
		 "messages": [
		  {"t":"1","msg": "<a href=\"javascript:void(0);\" onclick=\"set_para(\'沪铜1706\');\">铜1706</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'沪铜1707\');\">铜1707</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'沪铜1708\');\">铜1708</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'沪铜1709\');\">铜1709</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'沪铜1710\');\">铜1710</a><br><a href=\"javascript:void(0);\" onclick=\"set_para(\'沪铜1711\');\">铜1711</a><br>"}
		 ]}';
		break;
	case '沪铜1706':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码：CU1706<br>名称：沪铜1706<br>收盘：45900<br>成交量：128784<br>总金额：295.5亿<br>2017年6月2日压力：46050<br>2017年6月2日支撑：45750<br>2017年6月3日压力：46050<br>2017年6月3日支撑：45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	case '沪铜1707':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码:CU1707<br>名称:沪铜1706<br>收盘:45900<br>成交量:128784<br>总金额:295.5亿<br>2017年6月2日压力:46050<br>2017年6月2日支撑:45750<br>2017年6月3日压力:46050<br>2017年6月3日支撑:45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	case '沪铜1708':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码:CU1708<br>名称:沪铜1706<br>收盘:45900<br>成交量:128784<br>总金额:295.5亿<br>2017年6月2日压力:46050<br>2017年6月2日支撑:45750<br>2017年6月3日压力:46050<br>2017年6月3日支撑:45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	case '沪铜1709':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码:CU1709<br>名称:沪铜1706<br>收盘:45900<br>成交量:128784<br>总金额:295.5亿<br>2017年6月2日压力:46050<br>2017年6月2日支撑:45750<br>2017年6月3日压力:46050<br>2017年6月3日支撑:45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	case '沪铜1710':
		echo '{
		 "messages": [
		  {"t":"0",msg": "代码:CU1710<br>名称:沪铜1706<br>收盘:45900<br>成交量:128784<br>总金额:295.5亿<br>2017年6月2日压力:46050<br>2017年6月2日支撑:45750<br>2017年6月3日压力:46050<br>2017年6月3日支撑:45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	case '沪铜1711':
		echo '{
		 "messages": [
		  {"t":"0","msg": "代码:CU1711<br>名称:沪铜1706<br>收盘:45900<br>成交量:128784<br>总金额:295.5亿<br>2017年6月2日压力:46050<br>2017年6月2日支撑:45750<br>2017年6月3日压力:46050<br>2017年6月3日支撑:45750<br>"},
		  {"t":"1","msg":"<a href=\"javascript:void(0);\" onclick=\"set_para(\'铜\');\">您还想查询铜的其它合约吗?(Y)</a>"}
		 ]}';
		break;
	default:
		echo '{
		 "messages": [
		  {"msg": "您的关键词不太详细哦，再告诉小美一次吧!"}
		 ]}';
}
?>