# Implementation of select for files.
import posix

proc createFdSet(fd: var TFdSet, s: seq[TFileHandle], m: var int) =
  FD_ZERO(fd)
  for i in items(s):
    m = max(m, int(i))
    FD_SET(i, fd)

proc pruneFdSet(s: var seq[TFileHandle], fd: var TFdSet) =
  var i = 0
  var L = s.len
  while i < L:
    if FD_ISSET(s[i], fd) == 0'i32:
      s[i] = s[L-1]
      dec(L)
    else:
      inc(i)
  setLen(s, L)

proc timeValFromMilliseconds(timeout = 500): Ttimeval =
  if timeout != -1:
    var seconds = timeout div 1000
    result.tv_sec = seconds.int32
    result.tv_usec = ((timeout - seconds * 1000) * 1000).int32

proc select*(readfds, writefds, exceptfds: var seq[TFileHandle],
             timeout: int = 500): int {.tags: [FReadIO].} =
  ## Traditional select function. This function will return the number of
  ## sockets that are ready to be read from, written to, or which have errors.
  ## If there are none; 0 is returned.
  ## ``Timeout`` is in miliseconds and -1 can be specified for no timeout.
  ##
  ## A socket is removed from the specific ``seq`` when it has data waiting to
  ## be read/written to or has errors (``exceptfds``).
  var tv {.noInit.}: Ttimeval = timeValFromMilliseconds(timeout)

  var rd, wr, ex: TFdSet
  var m = 0
  createFdSet((rd), readfds, m)
  createFdSet((wr), writefds, m)
  createFdSet((ex), exceptfds, m)

  if timeout != -1:
    result = int(select(cint(m+1), addr(rd), addr(wr), addr(ex), addr(tv)))
  else:
    result = int(select(cint(m+1), addr(rd), addr(wr), addr(ex), nil))

  pruneFdSet(readfds, (rd))
  pruneFdSet(writefds, (wr))
  pruneFdSet(exceptfds, (ex))
