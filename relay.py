import sys, os, time
import ctypes

libpath = "."

if sys.version_info.major >= 3:
  def charpToString(charp):
     return str(ctypes.string_at(charp), 'ascii')
  def stringToCharp(s) :   
    return bytes(s, "ascii")
else:
  def charpToString(charp) :
     return str(ctypes.string_at(charp))
  def stringToCharp(s) :   
    return bytes(s)  #bytes(s, "ascii")
 
libfile = {'nt':   "usb_relay_device.dll", 
           'posix': "usb_relay_device.so",
           'darwin':"usb_relay_device.dylib",
           } [os.name]

#?? MAC => os.name == "posix" and sys.platform == "darwin"

devids = []
hdev = None

def exc(msg):  return Exception(msg)

def fail(msg) : raise exc(msg)
 
class L: pass   # Global object for the DLL
setattr(L, "dll", None)


def loadLib():
  if not L.dll :
    print("Loading DLL: %s" % ('/'.join([libpath, libfile])))
    try:
      L.dll = ctypes.CDLL( '/'.join([libpath, libfile]) )
    except OSError:  
      fail("Failed load lib")
  else:
    print("lib already open")


usb_relay_lib_funcs = [
  ("usb_relay_device_enumerate",               'h', None),
  ("usb_relay_device_close",                   'e', 'h'),
  ("usb_relay_device_open_with_serial_number", 'h', 'si'),
  ("usb_relay_device_get_num_relays",          'i', 'h'),
  ("usb_relay_device_get_id_string",           's', 'h'),
  ("usb_relay_device_next_dev",                'h', 'h'),
  ("usb_relay_device_get_status_bitmap",       'i', 'h'),
  ("usb_relay_device_open_one_relay_channel",  'e', 'hi'),
  ("usb_relay_device_close_one_relay_channel", 'e', 'hi'),
  ("usb_relay_device_close_all_relay_channel", 'e', None)
  ]


def getLibFunctions():
  assert L.dll
  libver = L.dll.usb_relay_device_lib_version()  
  print("%s version: 0x%X" % (libfile,libver))
  ret = L.dll.usb_relay_init()
  if ret != 0 : fail("Failed lib init!")
  ctypemap = { 'e': ctypes.c_int, 'h':ctypes.c_void_p, 'p': ctypes.c_void_p,
            'i': ctypes.c_int, 's': ctypes.c_char_p}
  for x in usb_relay_lib_funcs :
      fname, ret, param = x
      try:
        f = getattr(L.dll, fname)
        print(x)
      except Exception:  
        fail("Missing lib export:" + fname)
      ps = []
      if param :
        for p in param :
          ps.append( ctypemap[p] )
      f.restype = ctypemap[ret]
      f.argtypes = ps
      setattr(L, fname, f)
 

def openDevById(idstr):
  print("Opening " + idstr)
  print(stringToCharp(idstr))
  h = L.usb_relay_device_open_with_serial_number(stringToCharp(idstr), 5)
  if not h: fail("Cannot open device with id="+idstr)
  global numch
  numch = L.usb_relay_device_get_num_relays(h)
  if numch <= 0 or numch > 8 : fail("Bad number of channels, can be 1-8")
  global hdev
  hdev = h  
  print("Number of relays on device with ID=%s: %d" % (idstr, numch))


def closeDev():
  global hdev
  L.usb_relay_device_close(hdev)
  hdev = None

# finds devices /boards fills global devids list
def enumDevs():
  global devids
  devids = []
  enuminfo = L.usb_relay_device_enumerate()
  while enuminfo :
    idstrp = L.usb_relay_device_get_id_string(enuminfo)
    idstr = charpToString(idstrp)
    print(idstr)
    assert len(idstr) == 5
    if not idstr in devids : devids.append(idstr)
    else : print("Warning! found duplicate ID=" + idstr)
    enuminfo = L.usb_relay_device_next_dev(enuminfo)

  print("Found devices: %d" % len(devids))
  

def unloadLib():
  global hdev, L
  if hdev: closeDev()
  L.dll.usb_relay_exit()
  L.dll = None
  print("Lib closed")


def turn_on(num=2):
    loadLib()
    getLibFunctions()
    try:
      print("Searching for compatible devices")
      enumDevs()
      if len(devids) != 0 :
        openDevById(devids[0])
        # testR2()
        global numch, hdev
        if numch <=0 or numch > 8:
          fail("Bad number of channels on relay device!")
        st = L.usb_relay_device_get_status_bitmap(hdev) 
        if st < 0:  fail("Bad status bitmask")
        print("Relay num ch=%d state=%x" % (numch, st))
        ret = L.usb_relay_device_open_one_relay_channel(hdev,num)
        closeDev()
    finally:  
      unloadLib()


def turn_off(num=2):
    loadLib()
    getLibFunctions()
    try:
      print("Searching for compatible devices")
      enumDevs()
      if len(devids) != 0 :
        openDevById(devids[0])
        # testR2()
        global numch, hdev
        ret = L.usb_relay_device_close_one_relay_channel(hdev,num)
        closeDev()
    finally:  
      unloadLib()


  
if __name__ == "__main__" :
  # main()
  turn_on()
  time.sleep(3)
  turn_off()