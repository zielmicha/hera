import os
import osproc

const
  busyboxPath = "/bin/busybox"

proc shell(cmd: seq[string]) =
  let p = execProcess(cmd[0], cmd[1..cmd.len-1])

proc setupMounts() =
  makeDirectory("")
