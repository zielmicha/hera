import json, osproc, strtabs, streams
import jsontool, proxyclient, agentio

proc setupEnviron(message: PJsonNode): PStringTable =
  nil

proc spawnProc(message: PJsonNode): PProcess =
  let stderrToStdout = message.getString("stderr") == "stdout"
  let command = message.getString("command")
  var options: set[TProcessOption] = {}

  if stderrToStdout:
    options = options + {poStderrToStdout}

  var args: seq[string] = @[]
  if command == nil:
    for arg in message.getSubjson("args"):
      args.add arg.str
  else:
    args = @["/bin/sh", "-c", command]

  return startProcess(args[0], "/",
                      args[1..args.len-1],
                      setupEnviron(message),
                      options)

proc readAll(stream: PStream): string =
  result = ""
  while true:
    let data = stream.readStr 4096
    if data.len == 0:
      break
    result.add data

proc exec(message: PJsonNode): PJsonNode =
  let stderrToStdout = message.getString("stderr") == "stdout"
  let useChroot = message.getBool("chroot", true)
  let doSync = message.getBool("sync", false)
  result = %{"status": %"ok"}
  if doSync:
    let p = spawnProc(message)
    result["stdout"] = %(p.outputStream.readAll)
    if not stderrToStdout:
      result["stderr"] = %(p.errorStream.readAll)
  else:
    assert false

proc processMessage*(message: PJsonNode): PJsonNode =
  let msgType = message["type"].str
  case msgType:
    of "exec":
      return exec(message)
    of "synthetic_error":
      raise newException(E_Synch, "synthetic_error")
    else:
      return %{"status": %"UnknownMessageType"}
