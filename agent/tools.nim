import streams, posix, os

let textdigits = "0123456789abcdefghijklmnopqrstuwvxyz"

proc randToText(a: string): string =
  result = ""
  for ch in a:
    result.add textdigits[int(ch) mod textdigits.len]

proc randomIdent*: string =
  let urandom = newFileStream("/dev/urandom", fmRead)
  defer: urandom.close()
  return urandom.readStr(16).randToText

proc readAll*(fd: FileHandle): string =
  result = ""
  var buff = newString(4096)
  while true:
    let r = read(fd, buff.cstring.pointer, buff.len)
    if r == 0:
      break
    if r < 0:
      raiseOSError(osLastError())
    result.add buff[0..r-1]

proc readFileFixed*(filename: string): TaintedString =
  var f = open(filename)
  try:
    result = f.getFileHandle.readAll
  finally:
    close(f)

proc addEntropyRaw(data: cstring, size: cint): cint {.importc.}

proc addEntropy*(data: string) =
  if addEntropyRaw(data.cstring, data.len.cint) != 0:
    raiseOSError(osLastError())

when isMainModule:
  echo randomIdent()
