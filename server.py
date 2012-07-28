import os

import brukva
import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop

import settings


c = brukva.Client(host=settings.REDIS_HOST,
                  port=settings.REDIS_PORT)
c.connect()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class AddHandler(tornado.web.RequestHandler):
    def post(self):
        import ipdb;ipdb.set_trace()
        self.render("index.html")


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
    (r"/static", tornado.web.StaticFileHandler,
     dict(path=app_settings['static_path'])),
], **app_settings)


if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
