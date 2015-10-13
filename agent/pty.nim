import os, posix
import selectfile
import agentio
import forkpty

proc exitnow*(code: cint): void {.importc: "exit".}

proc checkedFork*: TPid =
  let res = fork()
  if res < 0:
    raiseOSError(osLastError())
  return res


template forkBlock*(b: stmt): stmt {.immediate.} =
  if checkedFork() == 0:
    b
    exitnow(1)

proc runCopier(amaster: FileHandle, files: openArray[FileHandle])

proc makeWinsize*(row: int, col: int): TWinsize =
  result.wsRow = cushort(row)
  result.wsCol = cushort(col)

proc checkedForkPty*(winsize: seq[int], files: seq[FileHandle]): TPid =
  let ret = forkpty(makeWinsize(winsize[0], winsize[1]))
  let pid = ret.pid
  let amaster = ret.master

  if pid != 0:
    forkBlock:
      # Fork a process that copies from master to given files
      runCopier(amaster, files)
    discard close(amaster)

  return pid

proc runCopier(amaster: FileHandle, files: openArray[FileHandle]) =
  finally:
    discard close(amaster)

  while true:
    var fds: TFdSet
    var maxfd = 0
    var readfds = @[amaster, files[0]]
    var writefds: seq[FileHandle] = @[]
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
        if read(inFd, addr buff, 1) != 1:
          return
        if write(outFd, addr buff, 1) != 1:
          return

when isMainModule:
  let p = checkedForkPty(@[40, 40],
    @[FileHandle(0), FileHandle(1), FileHandle(2)])
  if p == 0:
    discard execShellCmd("echo aaa; sleep 1; echo bbb; sh")
  else:
    var res: cint
    discard wait(res)
