import posix, os
import pty

export pty.forkBlock

proc cchroot(path: cstring): cint {.importc: "chroot", header: "<unistd.h>".}

proc checkedChroot(path: string) =
  if cchroot(path) < 0:
    raiseOsError(osLastError())

proc write*(fd: TFileHandle, data: string) =
  if write(fd, data.cstring, data.len) < 0:
    raiseOsError(osLastError())


proc checkedForkNopty(files: openarray[TFileHandle]): TPid =
  let res = checkedFork()
  if res == 0:
    # Close stdio
    for i in 0..2:
      discard close(cint(2))
    # Reopen FDs specified by parent
    for key, fd in files:
      discard dup2(cint(fd), cint(key))

  return res

proc startProcess*(args: seq[string], files: openarray[TFileHandle],
                   chroot: string=nil, ptySize: seq[int]=nil): TPid =
  let res = if ptySize != nil:
      checkedForkPty(ptySize, @files)
    else:
      checkedForkNopty(files)
  if res == 0:
    # Close old FDs
    for i in 3..1024:
      discard close(cint(i))
    # Chroot
    if chroot != nil:
      checkedChroot(chroot)
      discard chdir("/")
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
    raiseOsError(osLastError())
  return status
