import os, posix
import selectfile
import agentio

proc exitnow*(code: cint): void {.importc: "exit".}

proc checkedFork*: TPid =
  let res = fork()
  if res < 0:
    osError(osLastError())
  return res


template forkBlock*(b: expr) =
  if checkedFork() == 0:
    b()
    exitnow(1)

proc runCopier(amaster: TFileHandle, files: openarray[TFileHandle])

type
  TWinsize* = object
    ws_row*: cushort          # rows, in characters
    ws_col*: cushort          # columns, in characters
    ws_xpixel*: cushort       # horizontal size, pixels
    ws_ypixel*: cushort       # vertical size, pixels

proc forkpty*(amaster: ptr cint; name: cstring; termp: pointer; winp: TWinsize): cint {.
 importc.}

proc makeWinsize*(row: int, col: int): TWinsize =
  result.ws_row = cushort(row)
  result.ws_col = cushort(col)

proc checkedForkPty*(winsize: seq[int], files: seq[TFileHandle]): TPid =
  var amaster: cint = -1
  let pid = forkpty(addr amaster, nil, nil, makeWinsize(winsize[0], winsize[1]))
  if pid < 0 or amaster < 0:
    osError(osLastError())

  if pid != 0:
    forkBlock:
      # Fork a process that copies from master to given files
      runCopier(amaster, files)

  return pid

proc runCopier(amaster: TFileHandle, files: openarray[TFileHandle]) =
  while true:
    var fds: TFdSet
    var maxfd = 0
    var readfds = @[amaster, files[0]]
    var writefds: seq[TFileHandle] = @[]
    var errfds = @[amaster, files[0]]
    var timeout = -1
    discard selectfile.select(readfds, writefds, errfds, timeout)

    if errfds.len != 0:
      return

    if readfds.len != 0:
      for inFd in readfds:
        let outFd = if inFd == amaster: files[1]
                    else: amaster

        var buff: array[1, int]
        discard read(inFd, addr buff, 1)
        discard write(outFd, addr buff, 1)

when isMainModule:
  let p = checkedForkPty(@[40, 40],
    @[TFileHandle(0), TFileHandle(1), TFileHandle(2)])
  if p == 0:
    discard execShellCmd("echo aaa; sleep 1; echo bbb; sh")
  else:
    var res: cint
    discard wait(res)
