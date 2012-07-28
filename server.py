import os
import random
import hashlib

import brukva
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
from tornado.web import asynchronous

import settings


c = brukva.Client(host=settings.REDIS_HOST,
                  port=settings.REDIS_PORT)
c.connect()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class AddHandler(tornado.web.RequestHandler):
    def post(self):
        title = self.get_argument('title', '')
        report = self.get_argument('report', '')
        selected_sites = self.get_argument('selected_sites', '')
        description = self.get_argument('description', '')
        h = hashlib.sha1(str(random.random())).hexdigest()[:5]
        c.hmset('layer_%s' % h, {'report': report, 'title': title, 'sites': selected_sites, 'description': description})
        self.redirect('/layer/%s' % h)


class ViewLayer(tornado.web.RequestHandler):

    @asynchronous
    def get(self, layer_hash):
        data = c.hgetall('layer_%s' % layer_hash, self.process_data)

    def process_data(self, data):
        if not data:
            self.write('Not found')
        else:
            data['sites'] = data['sites'].split(',')
            print data
            self.render("view_layer.html", **data)


class MessagesCatcher(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessagesCatcher, self).__init__(*args, **kwargs)
        self.client = brukva.Client(host=settings.REDIS_HOST,
                                    port=settings.REDIS_PORT)
        self.client.connect()
        self.client.subscribe(settings.CHAT_KEY)

    def open(self):
        print "open"
        self.client.listen(self.on_message)

    def on_message(self, result):
        print "message"
        self.write_message(str(result.body))

    def close(self):
        print "close"
        self.client.unsubscribe(settings.CHAT_KEY)
        self.client.disconnect()


app_settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
}

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/track', MessagesCatcher),
    (r'/add', AddHandler),
    (r'/layer/(\w+)', ViewLayer),
    (r"/static", tornado.web.StaticFileHandler,
     dict(path=app_settings['static_path'])),
], **app_settings)


if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
