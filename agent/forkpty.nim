# forkpty reimplementation
import os, posix

type
  TWinsize* = object
    ws_row*: cushort          # rows, in characters
    ws_col*: cushort          # columns, in characters
    ws_xpixel*: cushort       # horizontal size, pixels
    ws_ypixel*: cushort       # vertical size, pixels

proc ltzeroerror(err: cint|TPid) =
  if err < 0:
    osError(osLastError())

proc unlockpt(fd: cint): cint {.importc.}
proc grantpt(fd: cint): cint {.importc.}
proc ioctl_wsize(d: cint, request: cint, winsize: ptr TWinsize): cint {.importc: "ioctl".}
proc ptsname_r(fd: cint, buf: cstring, buflen: int): cint {.importc.}

const TIOCSWINSZ*: cint = 21524

proc forkpty*(wsize: TWinsize): tuple[pid: TPid, master: cint] =
  # TODO: error checking
  var ptm: cint = open("/dev/ptmx", O_RDWR)
  ltzeroerror ptm
  ltzeroerror fcntl(ptm, F_SETFD, FD_CLOEXEC)
  ltzeroerror grantpt(ptm)
  ltzeroerror unlockpt(ptm)
  var wsizeForAddr = wsize
  ltzeroerror ioctl_wsize(ptm, TIOCSWINSZ, addr wsizeForAddr)
  var devname: array[0..1024 - 1, char]
  ltzeroerror ptsname_r(ptm, devname, sizeof((devname)))
  var pid: TPid = fork()
  ltzeroerror pid
  if pid == 0:
    ltzeroerror setsid()
    var pts: cint = open(devname, O_RDWR)
    ltzeroerror pts
    ltzeroerror dup2(pts, 0)
    ltzeroerror dup2(pts, 1)
    ltzeroerror dup2(pts, 2)
    ltzeroerror close(ptm)
    return (TPid(0), cint(-1))
  else:
    return (pid, ptm)

when isMainModule:
  var w: TWinsize
  w.ws_row = 20
  w.ws_col = 20
  w.ws_xpixel = 200
  w.ws_ypixel = 200
  let (pid, amaster) = forkpty(w)
