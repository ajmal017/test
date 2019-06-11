from websocket import create_connection
import simplejson as json
ws = create_connection("wss://api.tiingo.com/test")

subscribe = {
                'eventName':'subscribe',
                'eventData': {
                            'authToken': '021498e2ab08bcf6bdd864fff0792f403de8e64c'
                            }
                }

ws.send(json.dumps(subscribe))
while True:
    print(ws.recv())