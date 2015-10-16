---
title: API Reference

language_tabs:
  - raw

toc_footers:
  - <a href="http://github.com/zielmicha/hera">Hera Github</a>

search: true
---

# API Architecture

The user visibile part of Hera consists of two components:

* The [REST API](#the-api) (`api.hera.example`) - handles authrization and all sandbox actions
* The [proxy](#proxy) (`proxy.hera.example`) - proxies communication between you and the sandbox. This component is very simple - it's only purpose it to
provide named 'pipes' - an object to which one side can write and from which the other one can read.

# Authorization

```raw
Authorization: Basic dXNlcm5hbWU6ZWZlNzIyYmYyNzc2YzM3NjNhMzJkYWViYWU0MmJhY2E=
```

Login using HTTP basic auth. Use account name as login and API key as password.
You only need to send the authorization header to the main API (e.g. `api.hera.example`), not to
the proxy (e.g. `proxy.hera.example`).

# The API

## POST /sandbox/

### Input

```raw
POST /sandbox/

owner=me&memory=256&timeout=100&template=debian8

→

{"status": "ok", "id": "e0f6f2bc-40db-476e-bd58-3b21ba36fab4"}
```

| name     | description
| -------- | ------------ |
| owner    | target owner user (default: `me`) |
| memory   | memory allocation for sandbox (in MB) |
| timeout  | timeout in seconds |
| template | template ID or name |
| node_type | required node type to execute on (not implemented) |
| whole_node | whether the sandbox should execute on node as the only process |

### Asynchronous creation

<aside class="warning">
not implemented
</aside>

By default, attempting to create new sandbox when cluster doesn't have enough free resources will return ResourceNotAvailable error.
If you want Hera to queue your request instead, use `async` mode.


| name        | description
| --------    | ------------ |
| async       | if `true`, enables the asynchronous mode |
| webhook_url | Hera will POST this URL when sandbox is ready |
| webhook_secret | will be passed to the webhook as `secret` parameter |
| priority    | priority - the lower the better

#### Webhook parameters


| name       | description
| -----      | ----------
| secret     | the value from `webhook_secret`
| id         | id of the newly created sandbox


## POST /sandbox/:id/unpack

```raw
POST /sandbox/e0f6f2bc-40db-476e-bd58-3b21ba36fab4/unpack

target=/home/foo&archive_type=tar&compress_type=gz
→
{
  "input": {
    "http": "https://proxy.hera.example/stream/b1waljugrnquldlb",
    "websocket": "wss://proxy.hera.example/stream/b1waljugrnquldlb"
  },
  "output": {
    "http": "https://proxy.hera.example/stream/ukn5rqsbhvcnz53g",
    "websocket": "wss://proxy.hera.example/stream/ukn5rqsbhvcnz53g"
  },
  "status": "ok"
}

POST https://proxy.hera.example/stream/b1waljugrnquldlb
Content-Length: 16000

..archive data..


GET https://proxy.hera.example/stream/ukn5rqsbhvcnz53g
→
{"status": "ok"}

```

Start unpacking archive into a sandbox.

| name         | description
| -----        | ----------
| archive_type | archive type (`tar` or `zip`)
| compress_type| compressor type in case of `tar` archive (one of `zJja` or empty string)
| target       | target directory

The response will cotnain stream addresses. You should upload the archive data to the `input` stream and then
retrieve response from the `output` stream.

## POST /sandbox/:id/exec

```raw
POST /sandbox/e0f6f2bc-40db-476e-bd58-3b21ba36fab4/exec

args=["echo", "hello world"]

→
{
  "stderr": {
    "http": "https://proxy.hera.example/stream/slxbbqufg1q18ko0",
    "websocket": "wss://proxy.hera.example/stream/slxbbqufg1q18ko0"
  },
  "stdout": {
    "http": "https://proxy.hera.example/stream/j0c6thtt4mxtlvll",
    "websocket": "wss://proxy.hera.example/stream/j0c6thtt4mxtlvll"
  },
  "stdin": {
    "http": "https://proxy.hera.example/stream/uqljv051a44998tq",
    "websocket": "wss://proxy.hera.example/stream/uqljv051a44998tq"
  },
  "status": "ok"
}
```

Start a process in a sandbox.

| name         | description | example
| -----        | ----------  | --------
| args         | command to execute serialized as an JSON array | ["echo", "hello world"]
| command      | command which will be passed to shell (alternative to args) | echo 'hello world'
| pty_size     | if present, command will be executed in new PTY with that size | [80, 240]
| stderr       | if equal `stdout`, stderr will be redirected to stdout | stderr
| chroot       | if equal `false`, the command will be executed in the initial boot environment | false

Read and write to the returned streams to control the child.

## GET /template/

```raw
GET /template/

→

{
    "status": "ok",
    "templates": [
        {"id": 431, "name": "template-name", "public": false}
    ]
}
```

List templates.

## GET /template/:id


```raw
GET /template/5

→

{"status": "ok", "id": 431, "name": "template-name", "public": false}
```

Get template info.


## POST /template/:id

```raw
POST /template/5

public=false&name=my-new-name

→

{"status": "ok"}
```

Change template.

### Input

| name   | description | example
| ------ | ----------- | --------
| public | boolean     | false
| name   | string      | debian8

## GET /cluster/

```raw
GET /cluster/

→
{
  "status": "ok",
  "nodes": [
    {
      "address": ["127.0.0.1", 51447],
      "resources": {
        "slots": 1000,
        "memory": 7210.80078125
      }
    }
  ]
}
```

Returns cluster state.

# Proxy

The API sometimes returns stream URLs, like this: `{"http": "https://proxy.hera.example/stream/uqljv051a44998tq", "websocket": "wss://proxy.hera.example/stream/uqljv051a44998tq"}`.

As you can guess, the proxy supports two interfaces - HTTP and WebSocket. The HTTP interface is simpler to use, but you should only
use it when you intend to read/write whole data at once. The WebSocket interface supports interactive commands, such as shells.

## HTTP interface

To write data via HTTP interface, simply provide it as `POST` body. To read data, use `GET` on the same interface.

```raw
POST https://proxy.hera.example/stream/b1waljugrnquldlb
Content-Length: 11

hello world
```

```raw
GET https://proxy.hera.example/stream/b1waljugrnquldlb
```

## WebSocket interface

To use WebSocket interface, open WebSocket connection to the URL in the `websocket` field.
By default, the stream will not be closed when you close the WebSocket (this can lead to processes seemingly hang waiting for stream end).
If you want to close it, append `?close=true` to the URL.
The WebSocket will be opened by default in binary mode -- this can be a problem when using it from some browsers.
If you append `?wsframe=unicode`, the server will decode them (UTF-8) and send as text frames.

# Errors

| name   | description
| ------ | -----------
| ok     | no error
| ResourceNotAvailable      | cluster has not enough resources to fullfil your request at this time
| SandboxNoLongerAlive      | the sandbox has already finished its execution
| PermissionDenied          | you are not permitted to access this object
| MalformedRequest          | your request doesn't make sense
| NotEnoughMemoryRequested  | sandbox of this type needs more memory than you have requested
