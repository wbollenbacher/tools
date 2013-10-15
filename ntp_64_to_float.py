# Converter for NTP v4 64 bit timestamp
#    takes either 64-bit hexadecimal NTP value produced by port_agent (delta from 1/1/1900)
#    or floating point seconds value from data-product (delta from 1/1/1970)
#    and converts it to a date/time string

import time, sys

def Convert_64_bit_hex_to_seconds (hexValue):
    # high double-word is seconds, low double-word is fraction of a second
    # returned value seconds is a floating point
    seconds = (hexValue >> 32) + (((float) (hexValue & 0xffffffff)) / pow(2,32))
    return seconds

if __name__ == '__main__':
    # offset in seconds from 1/1/00 to 1/1/70
    DeltaOffset = 2208988800
    
    # check that there is only one option on the command line
    if len(sys.argv) != 2:
        print ("expecting one command line option, got %d" %(len(sys.argv)-1))
        sys.exit(1)
    
    # determine if there is a hex or floating point option
    strValue = sys.argv[1]
    if strValue.find('.') != -1:
        # got a floating point value
        try:
            seconds = float (strValue) / 1000
            print ("seconds = %s" %str(seconds)) 
            dateTime = time.ctime (seconds)
            print ("date = %s" %dateTime)
        except:
            print ("%s is not a floating point value" %strValue)
            sys.exit(1)            
    else:
        # got a hexadecimal value
        try:
            hexValue = int (strValue, 16)
            print ("Converting 64 bit hex value %X to seconds and date" %hexValue)
            seconds = Convert_64_bit_hex_to_seconds (hexValue)
            print ("Hex value %X = %s seconds" % (hexValue, str(seconds)))
            print ("seconds = %s" %str(seconds)) 
            print ("seconds adjusted = %s" %str(seconds - DeltaOffset)) 
            dateTime = time.ctime (seconds - DeltaOffset)
            print ("date = %s" %dateTime)
        except:
            print ("%s is not a hexadecimal value" %strValue)
            sys.exit(1)
    
