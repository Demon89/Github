# 小脚本用于爬取BT之家的电影种子 #


## 功能： ##

1、支持更新最新的BT种子信息到本地的文本数据库

2、支持查找电影的BT种子信息

3、支持下载电影的BT种子信息

## 实现方式： ##
利用urllib中的request请求需要爬取的页面获取html源码以后,利用正则过滤内容，把匹配到的信息保存到文本中，最后以文本数据库的方式保存电影的BT种子信息，以支持后续的查询电影以及下载电影的BT种子等.

## 引用的模块： ##
利用python内置的urllib,threading,sys,os,re以及三方的requests库


## 使用方法： ##

Low B小哥哥：
	
	Low B哥呀,不是这样玩的呀.

名称:

	这特么的是一个爬取小电影的bt种子

简介:

	<update [更新电影的初始页,更新电影的终止页]> <search电影名称> <download电影名称或者BT下载的地址>

描述:

	search:    查找的电影名称
	update:    更新本地BT电影库，可以加上起始、终止的页数，默认为前五页
	download:  下载的电影名称或者BT种子的URL地址，默认下载查找到的第一条匹配电影

示例：

	update    1　10
	search    速度与激情8
	download  速度与激情8

作者:

	Film Torrent Spider by Demon.

时间:
	
	2017/5/12 21:24:43 
