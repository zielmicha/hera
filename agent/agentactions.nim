import json, strtabs, streams, posix, os, sockets, strutils, osproc
import jsontool, proxyclient, agentio, process, tools

var
  proxyWsRemoteAddr*: string
  proxyHttpRemoteAddr*: string
  proxyLocalAddr*: string

proc setupEnviron(message: PJsonNode): PStringTable =
  nil

proc makeArgs(message: PJsonNode): seq[string] =
  let command = message.getString("command")

  var args: seq[string] = @[]
  if command == nil:
    for arg in message.getSubjson("args"):
      args.add arg.str
  else:
    args = @["/bin/sh", "-c", command]
  return args

type TPipe = tuple[procFd: TFileHandle, finish: proc(): PJsonNode]

proc makePipeSync(read: bool): TPipe =
  var fds: array[0..1, cint]
  if pipe(fds) < 0:
    raiseOsError(osLastError())
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
  let stdinPipe = makePipeNorm()
  let stdoutPipe = makePipeNorm()
  let errPipe = if not stderrToStdout: makePipeNorm()
                else: stdoutPipe # whatever
  return (stdinPipe, stdoutPipe, errPipe)

proc exec(message: PJsonNode): PJsonNode =
  log("exec begin")
  let stderrToStdout = message.getString("stderr") == "stdout"
  let doSync = message.getBool("sync", false)
  let useChroot = message.getBool("chroot", true)
  let ptySizeJson = message.getSubjson("pty_size")

  let ptySize =
    if ptySizeJson == nil:
      nil
    else:
      @[ptySizeJson[0].num.int, ptySizeJson[1].num.int]

  let args = makeArgs(message)
  var (stdin, stdout, stderr) = if doSync: makePipesSync()
                                else: makePipesNorm(stderrToStdout)
  if stderrToStdout:
    stderr = stdout

  let pid = startProcess(args,
                         files=[stdin.procFd, stdout.procFd, stderr.procFd],
                         chroot=if useChroot: "/mnt" else: nil,
                         ptySize=ptySize)

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
    let status = waitpid(pid)
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

proc unpack(message: PJsonNode): PJsonNode =
  let kind = message.getString("archive_type")
  var compress = message.getString("compress_type")
  if compress == nil:
    compress = ""
  if compress notin @["z", "J", "j", "a", ""]:
    return %{"status": %"InvalidCompressionFlag"}
  var target = message.getString("target")
  if target == nil:
    target = "/"
  var cmd: seq[string]
  if kind == "tar":
    cmd = @["/bin/busybox", "tar", "-" & compress & "x", "-C", "/mnt/" & target]
  elif kind == "zip":
    let id = randomIdent()
    cmd = @["/bin/busybox", "sh", "-c",
      "busybox cat > /mnt/$1; busybox unzip /mnt/$1 -qd /mnt/$2; busybox rm /mnt/$1" % [
         id, quoteShell(target)]]
  else:
    log("bad archive type: $1" % kind)
    return %{"status": %"UnknownArchiveType"}

  let stdin = makePipeNorm()
  let stderr = makePipeNorm()

  forkBlock:
    let pid = startProcess(cmd, files=[stdin.procFd, 1, 1])
    let status = waitpid(pid)
    log("wait returned $1" % [$status.wExitStatus])
    if wExitStatus(status) != 0:
      stderr.procFd.write($(%{"status": %"UnpackFailed"}))
    else:
      stderr.procFd.write($(%{"status": %"ok"}))
    log("written")

  discard stderr.procFd.close
  discard stdin.procFd.close
  return %{"status": %"ok", "input": stdin.finish(), "output": stderr.finish()}

proc processMessage*(message: PJsonNode): PJsonNode =
  let msgType = message["type"].str
  case msgType:
    of "exec":
      return exec(message)
    of "unpack":
      return unpack(message)
    of "prepare_for_death":
      return prepareForDeath()
    of "halt":
      halt()
      return %{"status": %"HaltFailed"}
    of "synthetic_error":
      raise newException(E_Synch, "synthetic_error")
    of "wait":
      return %{"status": %"ok"}
    else:
      return %{"status": %"UnknownMessageType"}

when isMainModule:
  let arg = parseJson(paramStr(1))
  let resp = exec(arg)
  echo resp
