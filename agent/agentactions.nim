import json, strtabs, streams, posix, os
import jsontool, proxyclient, agentio, process, tools

proc setupEnviron(message: PJsonNode): PStringTable =
  nil

proc makeArgs(message: PJsonNode): seq[string] =
  let command = message.getString("command")
  let useChroot = message.getBool("chroot", true)

  var args: seq[string] = @[]
  if command == nil:
    for arg in message.getSubjson("args"):
      args.add arg.str
  else:
    args = @["/bin/sh", "-c", command]
  return args

type TPipe = Tuple[procFd: TFileHandle, finish: proc(): string]

proc makePipeSync(read: bool): TPipe =
  var fds: array[0..1, cint]
  if pipe(fds) < 0:
    osError(osLastError())
  if not read:
    swap(fds[0], fds[1])

  proc finish(): string =
    if read:
      return nil
    else:
      let data = fds[1].readAll
      discard fds[1].close
      return data

  return (fds[0], finish)

proc makePipesSync(): auto =
  (makePipeSync(read=true), makePipeSync(read=false), makePipeSync(read=false))

proc makePipesNorm(stderrToStdout: bool): auto =
  makePipesSync()

proc exec(message: PJsonNode): PJsonNode =
  let stderrToStdout = message.getString("stderr") == "stdout"
  let doSync = message.getBool("sync", false)

  let args = makeArgs(message)
  var (stdin, stdout, stderr) = if doSync: makePipesSync()
                                else: makePipesNorm(stderrToStdout)
  if stderrToStdout:
    stderr = stdout

  let pid = startProcess(args, files=[stdin.procFd, stdout.procFd, stderr.procFd])

  discard stdin.procFd.close
  discard stdout.procFd.close
  if not stderrToStdout:
    discard stderr.procFd.close

  var response = %{"status": %"ok"}
  response["stdin"] = nullsafeJson(stdin.finish())
  response["stdout"] = nullsafeJson(stdout.finish())
  if not stderrToStdout:
    response["stderr"] = nullsafeJson(stderr.finish())
  if doSync:
    var status: cint
    if waitpid(pid, status, 0) < 0:
      osError(osLastError())
    response["status"] = %(wExitStatus(status))

  return response

proc processMessage*(message: PJsonNode): PJsonNode =
  let msgType = message["type"].str
  case msgType:
    of "exec":
      return exec(message)
    of "synthetic_error":
      raise newException(E_Synch, "synthetic_error")
    else:
      return %{"status": %"UnknownMessageType"}

when isMainModule:
  let arg = parseJson(paramStr(1))
  let resp = exec(arg)
  echo resp
