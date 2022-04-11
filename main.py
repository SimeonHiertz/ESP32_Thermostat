import machine, onewire, ds18x20, time
from oled import Write, GFX, SSD1306_I2C
from oled.fonts import ubuntu_mono_15

def init_oled():
    #Connects to OLED Display and returns: oled object and write object

    sda=machine.Pin(26)
    scl=machine.Pin(25)

    i2c=machine.SoftI2C(sda=sda, scl=scl)
    oled=SSD1306_I2C(128, 64, i2c)

    write15 = Write(oled, ubuntu_mono_15)
    return oled,write15


def do_connect():
    #Connects to network interface
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('SCHEIBENWELT', 'Rincewind')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    
class switch():
    def __init__(self, pin):
        self.led=machine.Pin(2,machine.Pin.OUT)
        self.output=machine.Pin(pin,machine.Pin.OUT)

    def switch_on(self):
        self.led.value(1)
        self.output.value(1)

    def switch_off(self):
        self.led.value(0)
        self.output(0)


class temp():
    def __init__(self,pin):
        #Connects DS18x20 single wire temperature sensor and returns 
        ds_pin = machine.Pin(pin)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        self.roms = self.ds_sensor.scan()
        print('Found DS devices: ', self.roms)
        self.rom=self.roms[-1]
        self.previous_reading=time.time()
        self.temp=0
        self.read_request=0

    def read_temperature(self):
        #reads temperature and returns value
        timenow=time.time()
        if self.read_request==0 and (timenow > (self.previous_reading+0.75)):
            self.ds_sensor.convert_temp()
            self.read_request=1

        if (timenow > (self.previous_reading+0.8)) and self.read_request == 1:
            self.temp=self.ds_sensor.read_temp(self.rom)
            self.previous_reading=timenow
            self.read_request=0
        return self.temp



oled,write15 = init_oled()
write15.text("Starting up", 0, 0)
oled.show()

Temperatursensor=temp(4)
maxtemp=80
Relais=switch(23)

#### MAINPART ####
oled.fill(0)
write15.text("connecting", 0, 0)
oled.show()
do_connect()
write15.text("successful!", 0, 15)
oled.show()
tmp=0
while True:
    try:
        oled.fill(0)
        temp=Temperatursensor.read_temperature()
        string_data=f"Temp: {temp:.3} C"
        write15.text(string_data, 0, 0)
        oled.show()
        print(f"Temperatur: {temp:.3}°C")
        tmp=temp
        if tmp<maxtemp:
            Relais.switch_on()
        else:
            Relais.switch_off()
        time.sleep_ms(500)
    except:
        print("Something went wrong.")
        oled.fill(0)
        write15.text("ERROR")
        oled.show()
        Relais.switch_off()