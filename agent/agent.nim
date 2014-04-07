import os, osproc, strutils, json

import agentactions, agentio

const
  busyboxPath = "/bin/busybox"

proc cchroot(path: cstring): cint {.importc: "chroot".}

proc chroot(path: string) =
  if cchroot(path) < 0:
    osError(osLastError())

proc busybox(cmd: seq[string]) =
  let p = startProcess(busyboxPath, args=cmd[0..cmd.len-1], options={poParentStreams})
  let code = p.waitForExit()
  if code != 0:
    raise newException(EIO, "call to $1 failed" % [cmd.repr])

proc mount(target: string, dev: string = nil, fs: string = nil) =
  assert fs != nil or dev != nil
  var dev = dev
  if dev == nil:
    dev = "nodev"
  var cmd = @["mount"]
  if fs != nil:
    cmd.add "-t"
    cmd.add fs
  cmd.add dev
  cmd.add target
  busybox(cmd)

proc setupMounts =
  createDir("/dev")
  mount(fs="devtmpfs", target="/dev")
  createDir("/proc")
  mount(fs="proc", target="/proc")
  createDir("/sys")
  mount(fs="sysfs", target="/sys")

proc processIncomingMessage =
  if isMessageAvailable():
    let message = readMessage()
    let resp = processMessage(message)
    writeMessage(resp)

proc main =
  setupMounts()
  openPort()
  while true:
    writeMessage(%{"outofband": %"heartbeat"})
    processIncomingMessage()

when isMainModule:
  try:
    main()
  finally:
    writeMessage(%{"outofband": %"internalerror"})
