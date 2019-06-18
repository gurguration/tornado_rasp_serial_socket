#!/bin/env python
#import sys
#sys.path.append('/home/alarm/testing_code')
#print(sys.path)
#exit()
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options
import os
import time
import worker
import multiprocessing
import json
 
define("port", default=9999, help="run on the given port", type=int)
 
clients = [] 

input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()


	

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class StaticFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('main.js')
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print ('new http connection')
        clients.append(self)
        self.write_message("connected")
 
    def on_message(self, message):
        print ('tornado received from client: %s' % json.dumps(message))
        input_queue.put(message)
 
    def on_close(self):
        print ('connection closed')
        clients.remove(self)


## check the queue for pending messages, and rely that to all connected clients



if __name__ == '__main__':
    ## start the serial worker in background (as a deamon)
    def checkQueue():
        if not output_queue.empty():
            message = output_queue.get()
            print ("tornado received from raspberry: ", message)
            for c in clients:
                c.write_message(message)
            
    sp = worker.SerialProcess(input_queue, output_queue)
    sp.daemon = True
    sp.start()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':  './'}),
            (r"/ws", WebSocketHandler)
        ]
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print ("Listening on port:", options.port)

    mainLoop = tornado.ioloop.IOLoop.instance()
    ## adjust the scheduler_interval according to the frames sent by the serial port
    scheduler_interval = 10
    scheduler = tornado.ioloop.PeriodicCallback(checkQueue, scheduler_interval, io_loop = mainLoop)
    scheduler.start()
    mainLoop.start()
