# -*- coding: utf-8 -*-
import urllib,urllib2,re,os,xbmcplugin,xbmcgui,xbmc
import xbmcaddon
import gzip, StringIO
import cookielib
from openload import get_dl_link
from bs4 import BeautifulSoup
import html5lib

__addonid__   = "plugin.video.mv6park"
__addon__     = xbmcaddon.Addon(id=__addonid__)
__addonicon__ = os.path.join( __addon__.getAddonInfo('path'), 'icon.png' )
__profile__   = xbmc.translatePath( __addon__.getAddonInfo('profile') )

cookieFile    = __profile__ + 'cookies.mv6park'
UserAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
html_template = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
%s
</body>
</html>
'''

VOD_LIST = [
        ('第1页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_1.html'),
        ('第2页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_2.html'),
        ('第3页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_3.html'),
        ('第4页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_4.html'),
        ('第5页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_5.html'),
        ('第6页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_6.html'),
        ('第7页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_7.html'),
        ('第8页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_8.html'),
        ('第9页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_9.html'),
        ('第10页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_10.html'),
        ('第11页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_11.html'),
        ('第12页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_12.html'),
        ('第13页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_13.html'),
        ('第14页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_14.html'),
        ('第15页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_15.html'),
        ('第16页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_16.html'),
        ('第17页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_17.html'),
        ('第18页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_18.html'),
        ('第19页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_19.html'),
        ('第20页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_20.html'),
        ('第21页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_21.html'),
        ('第22页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_22.html'),
        ('第23页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_23.html'),
        ('第24页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_24.html'),
        ('第25页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_25.html'),
        ('第26页','http://blog.sina.com.cn/s/article_sort_5661733206_10001_26.html'),
]

def getHttpData(url):
    print "getHttpData: " + url
    # setup proxy support
    proxy = __addon__.getSetting('http_proxy')
    type = 'http'

    if proxy <> '':
        ptype = re.split(':', proxy)
        if len(ptype)<3:
            # full path requires by Python 2.4
            proxy = type + '://' + proxy 
        else: type = ptype[0]
        httpProxy = {type: proxy}
    else:
        httpProxy = {}
    proxy_support = urllib2.ProxyHandler(httpProxy)
    
    # setup cookie support
    cj = cookielib.MozillaCookieJar(cookieFile)
    if os.path.isfile(cookieFile):
        cj.load(ignore_discard=False, ignore_expires=False)
    else:
        if not os.path.isdir(os.path.dirname(cookieFile)):
            os.makedirs(os.path.dirname(cookieFile))

    # create opener for both proxy and cookie
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPCookieProcessor(cj))
    charset=''
    req = urllib2.Request(url)
    req.add_header('User-Agent', UserAgent)

    try:
        response = opener.open(req)
        #response = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        httpdata = e.read()
    except urllib2.URLError, e:
        httpdata = "IO Timeout Error"
    else:
        httpdata = response.read()
        if response.headers.get('content-encoding', None) == 'gzip':
            httpdata = gzip.GzipFile(fileobj=StringIO.StringIO(httpdata)).read()
        charset = response.headers.getparam('charset')
        cj.save(cookieFile, ignore_discard=True, ignore_expires=True)
        response.close()

    httpdata = re.sub('\r|\n|\t', '', httpdata)
    match = re.compile('<meta.+?charset=["]*(.+?)"').findall(httpdata)
    if len(match):
        charset = match[0]
    if charset:
        charset = charset.lower()
        if (charset != 'utf-8') and (charset != 'utf8'):
            httpdata = httpdata.decode(charset, 'ignore').encode('utf8', 'ignore')

    return httpdata

##################################################################################
def addDir(name, url, mode, pic = '', isDir = True):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    li=xbmcgui.ListItem(name, '', pic, pic)
    li.setInfo( type="Video", infoLabels={ "Title": name } )
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=li,isFolder=isDir)

##################################################################################
# Main Menu
##################################################################################
def MainMenu():
    # add search item
    addDir('Search', '', '2')

    for v in VOD_LIST:
        name = v[0]
        url = v[1]
        addDir( name, url, '1')
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def showVideoLists(url):   
    #url = 'http://blog.sina.com.cn/s/article_sort_5661733206_10001_1.html'
    link = getHttpData(url)
    if link == None: return

    html = html_template % link
    soup = BeautifulSoup( html, 'html5lib')
    blog_title_list = soup.find_all("div", class_="blog_title")
    blog_content_list = soup.find_all("div", class_="content")

    for title, content in zip(blog_title_list, blog_content_list):
        url = title.a.get('href')
        name = title.a.text.encode('utf-8')
        thumb = ''

        img = content.find("img")
        if img is not None:
            thumb = img.get('src') if img.get('real_src') == None else img.get('real_src')

        addDir(name, url, '9', thumb)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def showEpisodeLists(url):   
    # url = 'http://blog.sina.com.cn/s/blog_1517731560102wjw1.html'
    data = getHttpData(url)
    if data == None: return

    matchli = re.compile('<a HREF="https://openload.co/f/(.+?)/?" TARGET="_blank">([\s\S]*?)</A>').findall(data)
    for match in matchli:
        file = match[0]
        title = match[1]
        
        # sometimes re cannot retrive the correct data
        # make sure the abnormal data won't impact the other ones
        if len(file) != 11: 
            xbmc.log("fanshaohua.fan: abnormal url -> %s" % url)
            xbmc.log("fanshaohua.fan: title -> %s" % title)
            continue

        dl_link = get_dl_link(file)

        li = xbmcgui.ListItem(title, iconImage = '', thumbnailImage = '')
        li.setInfo(type = "Video", infoLabels = {"Title":title})
        u = sys.argv[0]+"?mode=10"+"&name="+urllib.quote_plus(title)+"&url="+urllib.quote_plus(dl_link)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), u, li, True)
 
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def playVideo(name, url):
    playlist=xbmc.PlayList(1)
    playlist.clear()

    li = xbmcgui.ListItem(name, iconImage = '', thumbnailImage = '')
    li.setInfo(type = "Video", infoLabels = {"Title": name})

    playlist.add(url, li)

    xbmc.Player(1).play(playlist)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

def search():
    keyboard = xbmc.Keyboard()
    while True:
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_text = keyboard.getText()
            if not search_text:
                dialog = xbmcgui.Dialog()
                dialog.ok("Search", "输入内容未空!")
                return
            else:
                break
        else:
            break

    if keyboard.isConfirmed():
        url = 'http://e2mv.com/?s=vod-search-wd-%s.html' %  keyboard.getText()
        link = getHttpData(url)
        if link == None: return

        matchli = re.compile('<h1><a href="(.+?)" target="_blank"').findall(link)
        if len(matchli):
            queries = {'mode': '9', 'url': matchli[0]}
            pluginurl = sys.argv[0] + '?' + urllib.urlencode(queries)
            builtin = 'Container.Update(%s)' % (pluginurl)
            xbmc.log("fanshaohua.fan: %s" % builtin)
            xbmc.executebuiltin(builtin)
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok("Search", "未查找到相关内容!")


##################################################################################

params=get_params()
url=None
mode=None
name=None

try:
    mode=int(params["mode"])
except:
    pass
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
ctl = {
            None : ('MainMenu()'),
            1    : ('showVideoLists(url)'),
            2    : ('search()'),

            9    : ('showEpisodeLists(url)'),
            10   : ('playVideo(name,url)'),
      }
exec(ctl[mode])
