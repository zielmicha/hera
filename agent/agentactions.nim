import json, strtabs, streams, posix, os, sockets, strutils
import jsontool, proxyclient, agentio, process, tools

var
  proxyWsRemoteAddr*: string
  proxyHttpRemoteAddr*: string
  proxyLocalAddr*: string

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

type TPipe = Tuple[procFd: TFileHandle, finish: proc(): PJsonNode]

proc makePipeSync(read: bool): TPipe =
  var fds: array[0..1, cint]
  if pipe(fds) < 0:
    osError(osLastError())
  if not read:
    swap(fds[0], fds[1])

  proc finish(): PJsonNode =
    if read:
      return newJNull()
    else:
      let data = fds[1].readAll
      discard fds[1].close
      return %data

  return (fds[0], finish)

proc makePipesSync(): auto =
  (makePipeSync(read=true), makePipeSync(read=false), makePipeSync(read=false))

proc makePipeNorm(): TPipe =
  let url = "stream/"
  let id = randomIdent()
  var sock: TSocket = socket()
  let parsedAddr = proxyLocalAddr.split(':')
  sock.connect(parsedAddr[0], TPort(parsedAddr[1].parseInt))
  sock.send("id=$1 role=server\n" % id)

  proc finish(): PJsonNode =
    return %{
       "websocket": %(proxyWsRemoteAddr & url & id),
       "http": %(proxyHttpRemoteAddr & url & id)}

  return (TFileHandle(sock.getFd()), finish)

proc makePipesNorm(stderrToStdout: bool): auto =
  let stdPipe = makePipeNorm()
  let errPipe = if not stderrToStdout: makePipeNorm()
                else: stdPipe # whatever
  return (stdPipe, stdPipe, errPipe)

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
  response["stdin"] = stdin.finish()
  response["stdout"] = stdout.finish()
  if not stderrToStdout:
    response["stderr"] = stderr.finish()
  if doSync:
    var status: cint
    if waitpid(pid, status, 0) < 0:
      osError(osLastError())
    response["code"] = %(wExitStatus(status))

  return response

proc prepareForDeath: auto =
  # Kill all processes except for self (init)
  discard kill(-1, 9)
  # Umount disk and sync
  busybox(@["umount", "-l", "/mnt"])
  busybox(@["sync"])
  # Ready for being killed safely.
  return %{"status": %"ok"}

proc halt =
  writeFile("/proc/sysrq-trigger", "o\n")

proc processMessage*(message: PJsonNode): PJsonNode =
  let msgType = message["type"].str
  case msgType:
    of "exec":
      return exec(message)
    of "prepare_for_death":
      return prepareForDeath()
    of "halt":
      halt()
      return %{"status": %"HaltFailed"}
    of "synthetic_error":
      raise newException(E_Synch, "synthetic_error")
    else:
      return %{"status": %"UnknownMessageType"}

when isMainModule:
  let arg = parseJson(paramStr(1))
  let resp = exec(arg)
  echo resp
