import network

ap = network.WLAN(network.AP_IF)
ap.active(False)
gc.collect()
