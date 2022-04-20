from django.contrib.gis.geoip2 import GeoIP2


def get_location(meta):
    try:
        ip = meta.get('HTTP_X_REAL_IP')
    except:
        ip = meta.get('REMOTE_ADDR')
        
    g = GeoIP2()
    country = ''
    city = ''
    latitude = 0
    longitude = 0
    # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
    if str(ip) != '127.0.0.1' and ip:
        try:
            print g.city(ip)
            if g.city(ip)['country_code'] == 'MD':
                country = 'RO'
                city = 'Iasi'
                latitude = 47.1584549
                longitude = 27.6014418
            else:
                country = g.city(ip)['country_code']
                city = g.city(ip)['city']
                latitude = g.city(ip)['latitude']
                longitude = g.city(ip)['longitude']
        except:
            country = ''
            city = ''
    return country, city, latitude, longitude
