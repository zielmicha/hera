import json, selectfile, os, osproc, strutils

var
  controllerPort*: TFile

const
  busyboxPath = "/bin/busybox"

proc busybox*(cmd: seq[string]) =
  let p = startProcess(busyboxPath, args=cmd[0..cmd.len-1], options={poParentStreams})
  let code = p.waitForExit()
  if code != 0:
    raise newException(EIO, "call to $1 failed" % [cmd.repr])

proc writeMessage*(m: PJsonNode) =
  controllerPort.write(($m) & "\n")
  controllerPort.flushFile()

proc writeErrorMessage*(m: string) {.locks: 0.} =
  echo(m)
  writeMessage(%{"outofband": %"internalerror",
                 "stacktrace": %m})
  writeMessage(%{"status": %"InternalError",
                 "stacktrace": %m})

proc log*(message: string) =
  writeMessage(%{"outofband": %"log",
                 "line": %message})

proc isMessageAvailable*: bool =
  var readfd, writefd, exceptfd: seq[TFileHandle]
  readfd = @[controllerPort.fileHandle]
  writefd = @[]
  exceptfd = @[]
  return select(readfd, writefd, exceptfd, timeout=500) != 0

proc readMessage*: PJsonNode =
  parseJson(controllerPort.readLine)

proc openPort* =
  controllerPort = open("/dev/vport1p1", fmReadWrite, bufSize=0)
  errorMessageWriter = writeErrorMessage
