import posix, os

proc exitnow(code: cint): void {.importc: "exit".}

proc startProcess*(args: seq[string], files: openarray[TFileHandle]): TPid =
  let res = fork()
  if res < 0:
    osError(osLastError())
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
    # Exec
    let sysArgs = allocCStringArray(args)
    discard execvp(sysArgs[0], sysArgs)
    # error
    exitnow(13)

  return TPid(res)

proc wExitStatus*(status: cint): int =
  return (int(status) and 0xff00) shr 8
