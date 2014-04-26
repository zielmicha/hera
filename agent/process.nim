import posix, os

proc exitnow(code: cint): void {.importc: "exit".}

proc checkedFork*: TPid =
  let res = fork()
  if res < 0:
    osError(osLastError())
  return res

proc cchroot(path: cstring): cint {.importc: "chroot", header: "<unistd.h>".}

proc checkedChroot(path: string) =
  if cchroot(path) < 0:
    osError(osLastError())

proc write*(fd: TFileHandle, data: string) =
  if write(fd, data.cstring, data.len) < 0:
    osError(osLastError())

proc startProcess*(args: seq[string], files: openarray[TFileHandle],
                   chroot: string=nil): TPid =
  let res = checkedFork()
  if res == 0:
    # Close stdio
    for i in 0..2:
      discard close(cint(2))
    # Reopen FDs specified by parent
    for key, fd in files:
      discard dup2(cint(fd), cint(key))
    # Close old FDs
    for i in 3..1024:
      discard close(cint(i))
    # Chroot
    if chroot != nil:
      checkedChroot(chroot)
    # Exec
    let sysArgs = allocCStringArray(args)
    discard execvp(sysArgs[0], sysArgs)
    # error
    files[2].write("Couldn't spawn process: " & osErrorMsg(osLastError()) & "\n")
    exitnow(13)

  return TPid(res)

proc wExitStatus*(status: cint): int =
  return (int(status) and 0xff00) shr 8

proc waitpid*(pid: TPid, options: cint=0): cint =
  var status: cint
  if waitpid(pid, status, options) < 0:
    osError(osLastError())
  return status

template forkBlock*(b: expr) =
  if checkedFork() == 0:
    b()
    exitnow(1)
