# decode port_agent data files

import time, sys

SYNC_BYTES = b'\xa3\x9d\x7a'

LENGTH_SYNC_BYTES = len(SYNC_BYTES)
LENGTH_MESSAGE_TYPE = 1
LENGTH_PACKET_SIZE = 2
LENGTH_CHECKSUM = 2
LENGTH_TIMESTAMP = 8
LENGTH_HEADER = LENGTH_SYNC_BYTES + LENGTH_MESSAGE_TYPE + LENGTH_PACKET_SIZE + LENGTH_CHECKSUM + LENGTH_TIMESTAMP

PACKET_SIZE_OFFSET = LENGTH_SYNC_BYTES + LENGTH_MESSAGE_TYPE
CHECKSUM_OFFSET = PACKET_SIZE_OFFSET + LENGTH_PACKET_SIZE
TIMESTAMP_OFFSET = CHECKSUM_OFFSET + LENGTH_CHECKSUM

InputBfr = b''
BytesToRead = LENGTH_SYNC_BYTES
MessageType = 0
PacketSize = 0
Checksum = 0
TimeStamp = b''

MessageTypeStr = ['Data From Instrument',
                  'Data From Driver',
                  'Port Agent Command',
                  'Port Agent Status',
                  'Port Agent Fault',
                  'Instrument Command',
                  'Heartbeat',
                  'Pickled Data From Instrument',
                  'Pickled Data From Driver']

def Convert_64_bit_hex_to_seconds (hexValue):
    # high double-word is seconds, low double-word is fraction of a second
    # returned value seconds is a floating point
    seconds = (hexValue >> 32) + (((float) (hexValue & 0xffffffff)) / pow(2,32))
    return seconds


def ProcesByte (Byte):
    global InputBfr, BytesToRead, MessageType, PacketSize, Checksum, TimeStamp
    
    #print ("processing byte <%02X>" %ord(Byte))
    InputBfr += Byte
    #print ("InputBfr=<%s>" %InputBfr)
    
    if len(InputBfr) == BytesToRead:
        if BytesToRead == LENGTH_SYNC_BYTES:
            if InputBfr == SYNC_BYTES:
                #print ("!!!!!!!!!!!!!!!!!!!!!!!!!!! detected sync")
                BytesToRead = LENGTH_HEADER
            else:
                InputBfr = InputBfr[1:]
        elif BytesToRead == LENGTH_HEADER:
            MessageType = ord(InputBfr[LENGTH_SYNC_BYTES])
            PacketSize = (ord(InputBfr[PACKET_SIZE_OFFSET]) * 0xFF) + ord(InputBfr[PACKET_SIZE_OFFSET+1])
            Checksum = InputBfr[CHECKSUM_OFFSET:TIMESTAMP_OFFSET]
            TimeStamp = InputBfr[TIMESTAMP_OFFSET:]
            print ("MsgType=%d (%s), DataSize=%d, TimeStamp=%s" %(MessageType, MessageTypeStr[MessageType-1], PacketSize-LENGTH_HEADER, TimeStamp.encode('HEX').upper()))
            BytesToRead += PacketSize - LENGTH_HEADER
        else:
            Data = InputBfr[LENGTH_HEADER:]
            print "Packet Data = <%s>" %Data.encode('HEX').upper(),
            try:
                Data.decode('ascii')
            except UnicodeDecodeError:
                pass
            else:
                print ", <%s>" %Data,           
            print ("\n")
            InputBfr = b''
            BytesToRead = LENGTH_SYNC_BYTES


if __name__ == '__main__':
    # offset in seconds from 1/1/00 to 1/1/70
    DeltaOffset = 2208988800
    NumberOfBytesRead = 0
    
    # check that there is only one option on the command line
    if len(sys.argv) != 2:
        print ("expecting one command line option, got %d" %(len(sys.argv)-1))
        sys.exit(1)
    
    FileName = sys.argv[1]
    
    with open (FileName, "rb") as f:
        while True:
            ByteRead = f.read(1)
            if not ByteRead:
                break
            NumberOfBytesRead += 1
            #if NumberOfBytesRead > 30:
            #    break
            ProcesByte (ByteRead)
    
    print ("total bytes processed = %d" %NumberOfBytesRead)
