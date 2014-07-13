import os, strutils, json, strtabs

import agentactions, agentio, tools

var
  requestedDiskFormat = false

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
  agentactions.proxyWsRemoteAddr = table["hera.proxy_ws_remote"]
  agentactions.proxyHttpRemoteAddr = table["hera.proxy_http_remote"]
  agentactions.proxyLocalAddr = table["hera.proxy_local"]
  requestedDiskFormat = table["hera.format_disk"] == "true"

proc setupMounts =
  createDir("/dev")
  mount(fs="devtmpfs", target="/dev")
  createDir("/dev/pts")
  mount(fs="devpts", target="/dev/pts")
  createDir("/proc")
  mount(fs="proc", target="/proc")
  createDir("/sys")
  mount(fs="sysfs", target="/sys")

proc prepareDisk =
  if requestedDiskFormat:
    busybox(@["mkfs.ext2", "/dev/vda"])
  createDir("/mnt")
  mount(dev="/dev/vda", target="/mnt")

  createDir("/mnt/dev")
  mount(fs="devtmpfs", target="/mnt/dev")
  createDir("/mnt/dev/pts")
  mount(fs="devpts", target="/mnt/dev/pts")
  createDir("/mnt/proc")
  mount(fs="proc", target="/mnt/proc")
  createDir("/mnt/sys")
  mount(fs="sysfs", target="/mnt/sys")

proc processIncomingMessage =
  if isMessageAvailable():
    let message = readMessage()
    let resp = processMessage(message)
    writeMessage(resp)

proc setupDefaultEnv =
  putEnv("TERM", "xterm")
  putEnv("PATH", "/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/games")
  putEnv("LANG", "en_US.UTF-8")
  putEnv("USER", "root")

proc main =
  setupMounts()
  openPort()
  setupOptions()
  prepareDisk()
  setupDefaultEnv()
  while true:
    writeMessage(%{"outofband": %"heartbeat"})
    processIncomingMessage()

when isMainModule:
  try:
    main()
  finally:
    writeMessage(%{"outofband": %"internalerror"})
