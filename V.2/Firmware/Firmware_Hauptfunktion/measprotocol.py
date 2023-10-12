import datetime

## Board status 
STA_OK = 0x00
STA_ERR_CHECKSUM = 0x01
STA_ERR_SERIAL = 0x02
STA_ERR_CHECK_OUT_LIMIT = 0x03
STA_ERR_CHECK_LOW_LIMIT = 0x04
STA_ERR_DATA = 0x05

def do_protocol(name,messreihe,distance,last_operate_status,strength,temp):
    
    if last_operate_status == STA_OK:
        d = "%d" %distance
    elif last_operate_status == STA_ERR_CHECKSUM:
        d = "ERROR"
    elif last_operate_status == STA_ERR_SERIAL:
        d = "Serial open failed!"
    elif last_operate_status == STA_ERR_CHECK_OUT_LIMIT:
        d = "Above the upper limit: %d" %distance
    elif last_operate_status == STA_ERR_CHECK_LOW_LIMIT:
        d = "Below the lower limit: %d" %distance
    elif last_operate_status == STA_ERR_DATA:
        d = "No data!"
    
    x = datetime.datetime.now()
    #a = x.strftime("%Y")+"-"+x.strftime("%m")+"-"+x.strftime("%d")
    a = x.strftime("%Y-%m-%d")
    b = x.strftime("%H:%M:%S:%f")[:-3]
    c = messreihe
    f = open(name+".csv", "a")
    f.write("{},{},{},{},{}".format(c, a, b, d, "mm"))
    if strength > 0:
        f.write(",{}".format(strength))
    if temp > 0:
        f.write(",{}".format(temp))
    f.write("\n")
    f.close()

if __name__ == "__main__":

    do_protocol("test",1.1,100)