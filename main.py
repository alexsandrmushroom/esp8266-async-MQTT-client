import uasyncio
from machine import Pin
import json, time
import ubinascii
from umqttsimple import MQTTClient

counter  = 0    
status_mqtt = 0

'''импорт переменных из конфиг файла'''
from config import mqtt_config
from config import topic_sub
from config import topic_pub
from config import wifi_config
from config import pin

'''пины на выход'''
led_esp = Pin(pin["led_esp"], Pin.OUT)

'''пины на вход'''
#button = Pin(pin["button"], Pin.IN)

import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = network.WLAN().config('mac')
mac_hex = ':'.join('{:02x}'.format(byte) for byte in mac)
print(f'MAC адрес: {mac_hex}')

'''подключчение к WIFI'''
async def connect():
    while True:
        if not wlan.isconnected():
            print('Поиск и подключение к Wi-Fi сети...')
            list_wlan = wlan.scan()
            for network in list_wlan:
                ssid = network[0].decode()
                if ssid == wifi_config['ssid']:
                    print('Wi-Fi сеть для подключения найдена')
                    wlan.connect(wifi_config['ssid'], wifi_config['password'])
                    await uasyncio.sleep( 3 ) 
                    print('информация о подключении', wlan.ifconfig())
                    
                    break
            else:
                print('Wi-Fi сеть для подключения не найдена')
        else:
            print('Сеть Wi-Fi подключена')
            #print('информация о подключении', wlan.ifconfig())
        await uasyncio.sleep( 10 )


def pub_msg(topic, msg, retain):
    global status_mqtt
    try:
        client.publish(topic, msg, retain)
    except:
        status_mqtt = 0
        print('eroor pub mqtt msg')


def sub_cb(topic, msg):
    print((topic, msg))



        
        
        

'''проверка сообщений'''
async def check_m():
    global status_mqtt
    while True:
        if status_mqtt == 1:
            try:
                client.check_msg()
            except:
                status_mqtt = 0
        else:
            pass
        await  uasyncio.sleep_ms(300 )

'''основной цикл'''
async def main():
    global counter, status_mqtt
    while True:
        counter +=1
        json_str = json.dumps({'count': counter, 'mqtt': status_mqtt})
        print(json_str)
        if status_mqtt == 1 : pub_msg(topic_pub, json_str, retain = False)
        await  uasyncio.sleep ( 1 )

'''подключене к брокеру и подписка к на топики'''
def connect_and_subscribe():
    try:
        global status_mqtt
        client = MQTTClient(mqtt_config['client_id'], mqtt_config['mqtt_server'],mqtt_config['port'], mqtt_config['user'], mqtt_config['password'])
        client.set_callback(sub_cb)
        client.connect()
        for item in topic_sub:
            print(f"topic sub: {topic_sub[item]}")
            client.subscribe(topic_sub[item])
        print('Connected to %s MQTT broker' % (mqtt_config['mqtt_server']))
        status_mqtt = 1
        return client
    except Exception as e:
        status_mqtt = 0
        print(f'connect mqqt broker error')
        client.disconnect()
        
async def connect_mqtt():
    global status_mqtt, client
    while True:
        if wlan.isconnected() == False:
            status_mqtt = 2
            print('no connected wi-fi')
        else:
            if status_mqtt == 2:status_mqtt = 0
        if status_mqtt == 0:
            try:
                client = connect_and_subscribe()
            except Exception as e:
                print(f'{e}')
        elif status_mqtt == 2:
            pass
        await  uasyncio.sleep ( 1 )



'''blinkv LED esp8266'''
async def led_ping():
    state = 0
    while True:
        led_esp.value(state)
        state = 1 - state
        await  uasyncio.sleep_ms ( 700 )
    
        

        

loop = uasyncio.get_event_loop()
loop.create_task(check_m())
loop.create_task(main())
loop.create_task(connect())
loop.create_task(connect_mqtt())
loop.create_task(led_ping())
loop.run_forever()


