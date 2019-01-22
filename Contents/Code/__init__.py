from datetime import date, timedelta
import re

def Start():
  ObjectContainer.title1 = 'LA7'
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36'

@handler('/video/la7', 'LA7', thumb = 'La7.jpg', art = 'La7.jpg')
def MainMenu():
  oc = ObjectContainer()
  html = HTML.ElementFromURL('http://www.la7.it/dirette-tv')
  src = html.xpath('//script[contains(.,"var vS")]/text()')[0].strip()
  src = src.replace("var vS = '", "", 1)
  src = src.replace("';", "", 1)
  oc.add(Show(
    url = src,
    title = "Live"
  ))
  for x in range(7):
    ddd = date.today() - timedelta(x)
    oc.add(DirectoryObject(
      key = Callback(ReplayList, title = ddd.strftime('%A %d %B %Y'), inc = x),
      title = ddd.strftime('%A %d %B %Y')
    ))
  return oc


@route('/video/la7/replaylist')
def ReplayList(title, inc):
  pattern = re.compile(r'"(http:[^"]*\.m3u8)"', re.IGNORECASE)
  oc = ObjectContainer(title2 = title)
  html = HTML.ElementFromURL('http://www.la7.it/rivedila7/{}/LA7'.format(inc))
  for item in html.xpath('//div[@class="palinsesto_row             disponibile clearfix"]'):
    title = '[{}] {}'.format(item.xpath('.//div[@class="orario"]/text()')[0], item.xpath('.//div[@class="titolo clearfix"]/a/text()')[0]).decode('utf-8')
    url = item.xpath('.//div[@class="titolo clearfix"]/a')[0];
    href = url.get('href');
    if not href.startswith('http'):
      href = 'http://www.la7.it{}'.format(href)
    Log(href)
    for m in re.finditer(pattern, HTTP.Request(href).content):
      Log('Add {}, {}'.format(title, m.group(1)))
      oc.add(Show(
        url = m.group(1).decode('utf-8'),
        title = title
      ))
  return oc


@route('/video/la7/show', include_container = bool)
def Show(url, title, include_container = False, **kwargs):
  vco = VideoClipObject(
    key = Callback(Show, url = url, title = title, include_container = True),
    rating_key = url,
    title = title,
    items = [
      MediaObject(
        protocol = Protocol.HLS,
        container = Container.MP4,
        video_codec = VideoCodec.H264,
        audio_codec = AudioCodec.AAC,
        audio_channels = 2,
        optimized_for_streaming = True,
        parts = [
          PartObject(
            key = HTTPLiveStreamURL(url = Callback(Play, url = url))
          )
        ],
      )
    ]
  )
  if include_container:
    return ObjectContainer(objects = [vco])
  else:
    return vco

@indirect
@route('/video/la7/play.m3u8')
def Play(url, **kwargs):
  return IndirectResponse(VideoClipObject, key = url)
