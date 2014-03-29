import os
import osproc
import strutils

const
  busyboxPath = "/bin/busybox"

var
  controllerPort: TFile

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
  createDir("/target")
  #mount(dev="/dev/vda", target="/target")

proc openPort =
  controllerPort = open("/dev/vport0p1", fmReadWrite)
  controllerPort.write("init\n")
  controllerPort.flushFile()

proc main =
  setupMounts()
  openPort()
  busybox(@["sh"])

when isMainModule:
  main()
