import json, selectfile

var
  controllerPort*: TFile

proc writeMessage*(m: PJsonNode) =
  controllerPort.write(($m) & "\n")
  controllerPort.flushFile()

proc writeErrorMessage*(m: string) =
  writeMessage(%{"outofband": %"internalerror",
                 "stacktrace": %m})
  writeMessage(%{"status": %"InternalError",
                 "stacktrace": %m})

proc log*(message: string) =
  writeMessage(%{"outofband": %"log",
                 "line": %message})

proc isMessageAvailable*: bool =
  var readfd, writefd, exceptfd: seq[TFile]
  readfd = @[controllerPort]
  writefd = @[]
  exceptfd = @[]
  return select(readfd, writefd, exceptfd, timeout=500) != 0

proc readMessage*: PJsonNode =
  parseJson(controllerPort.readLine)

proc openPort* =
  controllerPort = open("/dev/vport0p1", fmReadWrite, bufSize=0)
  errorMessageWriter = writeErrorMessage
