import streams, posix, os

let textdigits = "0123456789abcdefghijklmnopqrstuwvxyz"

proc randToText(a: string): string =
  result = ""
  for ch in a:
    result.add textdigits[int(ch) mod textdigits.len]

proc randomIdent*: string =
  let urandom = newFileStream("/dev/urandom", fmRead)
  finally: urandom.close()
  return urandom.readStr(16).randToText

proc readAll*(fd: TFileHandle): string =
  result = ""
  var buff = newString(4096)
  while true:
    let r = read(fd, buff.cstring.pointer, buff.len)
    if r == 0:
      break
    if r < 0:
      osError(osLastError())
    result.add buff[0..r-1]

proc readFileFixed*(filename: string): TaintedString =
  var f = open(filename)
  try:
    result = f.fileHandle.readAll
  finally:
    close(f)

when isMainModule:
  echo randomIdent()
