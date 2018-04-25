

import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

def url_pos(txt):

  query = 'http://10.9.46.102:8080/semantic/analysis?userid=keo&text=%s'%(txt)
  try:
    res = requests.get(query,timeout=0.06)
    if res.content:
      return eval(res.content)['data']
  except (IOError ,ZeroDivisionError),e:
    return 'None'