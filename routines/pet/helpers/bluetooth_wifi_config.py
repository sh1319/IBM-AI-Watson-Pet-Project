from bluetooth import *
import subprocess
import time
import os

wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "

def create_wifi_config(SSID, password):
    #setting up file contents
    config_lines = [
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'update_config=1',
        'country=GB',
        '\n',
        'network={',
        '\tssid="{}"'.format(SSID),
        '\tpsk="{}"'.format(password),
        '}'
        ]
    config = '\n'.join(config_lines)
    
    #display additions
    print(config)
    
    #give access and writing. may have to do this manually beforehand
    os.popen("sudo chmod a+w /etc/wpa_supplicant/wpa_supplicant.conf")
    
    #writing to file
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        wifi.write(config)
    
    #displaying success
    print("wifi config added")

def handle_client(client_sock) :
    # get ssid
    sample = "test1!test2!test3!test4"
    client_sock.send(sample)
    print ("Waiting for SSID...")


    ssid = client_sock.recv(1024)
    if ssid == '' :
        return

    print ("ssid received")
    print (ssid)

    # get psk
    client_sock.send("waiting-psk!")
    print ("Waiting for PSK...")


    psk = client_sock.recv(1024)
    if psk == '' :
        return

    print ("psk received")

    print (psk)

    ip_address = create_wifi_config(ssid.decode('utf-8'), psk.decode('utf-8'))

    #used to send ip address here
    client_sock.send("success!")

    return

def try_wifi_setup():
    try:
        while True:
            server_sock=BluetoothSocket( RFCOMM )
            server_sock.bind(("",PORT_ANY))
            server_sock.listen(1)

            port = server_sock.getsockname()[1]

            uuid = "643dddc4-5e4f-4072-ab90-6668d38c146d"

            advertise_service( server_sock, "RPi Wifi config",
                               service_id = uuid,
                               service_classes = [ uuid, SERIAL_PORT_CLASS ],
                               profiles = [ SERIAL_PORT_PROFILE ])


            print ("Waiting for connection on RFCOMM channel %d" % port)

            client_sock, client_info = server_sock.accept()
            print ("Accepted connection from ", client_info)

            handle_client(client_sock)

            client_sock.close()
            server_sock.close()

            # finished config
            print ('Finished configuration. Rebooting.\n')
            os.popen("sudo reboot")

    except (KeyboardInterrupt, SystemExit):
        print ('\nExiting\n')
