import ubinascii, machine
wifi_config = {
    'ssid':'',
    'password':''
    }

pin = {
    "led_esp" : 2
    }

mqtt_config = {
    'client_id' : b"esp8266_" + ubinascii.hexlify(machine.unique_id()),
    'mqtt_server' : '192.168.1.1',
    'port' : 1883,
    'user' : 'user',
    'password' : 'password'
    } 

topic_sub = {
    1 : b"odin",
    2 : b"dva",
    3 : b"tri"
    }
topic_pub = "/esp8266"
