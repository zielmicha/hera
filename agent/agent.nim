import os, osproc, strutils, json, strtabs

import agentactions, agentio, tools

const
  busyboxPath = "/bin/busybox"

var
  requestedDiskFormat = false

proc cchroot(path: cstring): cint {.importc: "chroot".}

proc chroot(path: string) =
  if cchroot(path) < 0:
    osError(osLastError())

proc busybox(cmd: seq[string]) =
  let p = startProcess(busyboxPath, args=cmd[0..cmd.len-1], options={poParentStreams})
  let code = p.waitForExit()
  if code != 0:
    raise newException(EIO, "call to $1 failed" % [cmd.repr])

proc parseKernelCmdline(line: string): PStringTable =
  result = newStringTable()
  for part in line.strip.split(' '):
    let s = part.split('=')
    if s.len == 2:
      result[s[0]] = s[1]

proc getKernelCmdline: PStringTable =
  readFileFixed("/proc/cmdline").parseKernelCmdline

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

proc setupOptions =
  let table = getKernelCmdline()
  agentactions.proxyRemoteAddr = table["hera.proxy_remote"]
  agentactions.proxyLocalAddr = table["hera.proxy_local"]
  requestedDiskFormat = table["hera.format_disk"] == "true"

proc setupMounts =
  createDir("/dev")
  mount(fs="devtmpfs", target="/dev")
  createDir("/proc")
  mount(fs="proc", target="/proc")
  createDir("/sys")
  mount(fs="sysfs", target="/sys")

proc prepareDisk =
  if requestedDiskFormat:
    busybox(@["mkfs.ext2", "/dev/vda"])
  createDir("/mnt")
  mount(dev="/dev/vda", target="/mnt")

proc processIncomingMessage =
  if isMessageAvailable():
    let message = readMessage()
    let resp = processMessage(message)
    writeMessage(resp)

proc main =
  setupMounts()
  openPort()
  setupOptions()
  prepareDisk()
  while true:
    writeMessage(%{"outofband": %"heartbeat"})
    processIncomingMessage()

when isMainModule:
  try:
    main()
  finally:
    writeMessage(%{"outofband": %"internalerror"})
