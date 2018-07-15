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
  Log(' --> Final stream la7: %s' % (src))
  oc.add(Show(
    src = src,
    title = "Live"
  ))
  return oc


@route('/video/la7/show', include_container = bool)
def Show(src, title, include_container = False, **kwargs):
  vco = VideoClipObject(
    key = Callback(Show, src = src, title = title, include_container = True),
    rating_key = src,
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
            key = HTTPLiveStreamURL(Callback(Play, src = src))
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
def Play(src, **kwargs):
  return IndirectResponse(VideoClipObject, key = src)
