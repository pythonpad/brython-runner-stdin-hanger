import asyncio
import sys
import random
import string
from aiohttp import web

def get_random_string(k=16): 
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))

class Handler:
    def __init__(self):
        self.store = {}
        self.headers = {'Access-Control-Allow-Origin': '*'}

    async def handle_sleep(self, request):
        duration_param = request.rel_url.query['duration']
        try:
            duration = min(float(duration_param), 60)
            await asyncio.sleep(duration)
            return web.Response(text='%.2f' % duration, headers=self.headers)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            return web.Response(text='-1', headers=self.headers)

    async def handle_open_slot(self, request):
        while True:
            key = get_random_string()
            if key not in self.store:
                self.store[key] = None
                return web.Response(text=key, headers=self.headers)
    
    async def handle_write_slot(self, request):
        key = request.match_info.get('key')
        data = await request.text()
        if key in self.store:
            self.store[key] = data
            return web.Response(text=key, headers=self.headers)
        else:
            raise web.HTTPNotFound()

    async def handle_read_slot(self, request):
        key = request.match_info.get('key')
        while True:
            if key in self.store:
                if self.store[key] is None:
                    await asyncio.sleep(1)
                else:
                    data = self.store[key]
                    del self.store[key]
                    return web.Response(text=data, headers=self.headers)
            else:
                raise web.HTTPNotFound()

def main():
    host = 'localhost'
    port = '9095'
    if len(sys.argv) > 1:
        config = sys.argv[1]
        if ':' in config:
            host, port = config.split(':')
        elif '.' in config:
            host = config
        else:
            port = config

    web.run_app(app, host=host, port=int(port))

handler = Handler()
app = web.Application()
app.add_routes([
    web.get('/hanger/sleep/', handler.handle_sleep),
    web.post('/hanger/open/', handler.handle_open_slot),
    web.post('/hanger/{key}/write/', handler.handle_write_slot),
    web.post('/hanger/{key}/read/', handler.handle_read_slot),
])

if __name__ == '__main__':
    main()