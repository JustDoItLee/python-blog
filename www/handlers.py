#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'lz'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

from www.coroweb import get, post

from www.models import User, Comment, Blog, next_id


@get('/')
def index(request):
    summary1 = '用户中心是几乎每一个公司必备的基础服务，用户注册、登录、信息查询与修改都离不开用户中心。当数据量越来越大时，需要多用户中心进行水平切分。最常见的水平切分方式，按照userId取模分库：'
    summary2 = 'QR码属于矩阵式二维码中的一个种类，由DENSO(日本电装)公司开发，由JIS和ISO将其标准化。QR码的样子其实在很多场合已经能够被看到了，我这还是贴个图展示一下：'
    summary3 = '最近这段时间折腾了一下WebRTC，这两天终于是抽了时间把WebRTC搞定了，去年就想弄的，但是确实没时间。看了网上的https://apprtc.appspot.com/的例子（可能需要翻墙访问），这个例子是部署在Google App Engine上的应用程序，依赖与GAE的环境，后台的语言是python，而且还依赖Google App Engine Channel API，所以无法在本地运行，也无法扩展。费了一番功夫研读了例子的python端的源代码，决定用Java实现，Tomcat7之后开始支持WebSocket，打算用WebSocket代替Google App Engine Channel API实现前后台的通讯，在整个例子中Java+WebSocket起到的作用是负责客户端之间的通信，并不负责视频的传输，视频的传输依赖于WebRTC。'
    blogs = [
        Blog(id='1', name='userId分库，怎么通过其他字段查询', summary=summary1, created_at=time.time() - 120),
        Blog(id='2', name='Java基于zxing生成二维码demo', summary=summary2, created_at=time.time() - 3600),
        Blog(id='3', name='Java使用websocket和WebRTC实现视频通话', summary=summary3, created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }
