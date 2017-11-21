#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from www.apis import APIValueError, APIError

__author__ = 'lz'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

from www.coroweb import get, post
from aiohttp import web
from www.models import User, Comment, Blog, next_id
from www.config import configs

COOKIE_NAME = 'pysession'
_COOKIE_KEY = configs.session.secret


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
async def index(request):
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


@get('/register')
async def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
async def signin():
    return {
        '__template__': 'signin.html'
    }


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
async def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r
