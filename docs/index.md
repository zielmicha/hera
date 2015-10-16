---
title: API Reference

language_tabs:
  - raw

toc_footers:
  - <a href="http://github.com/zielmicha/hera">Hera Github</a>

search: true
---

# Authorization

```raw
Authorization: Basic dXNlcm5hbWU6ZWZlNzIyYmYyNzc2YzM3NjNhMzJkYWViYWU0MmJhY2E=
```

Login using HTTP basic auth. Use account name as login and API key as password.

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

# Errors

| name   | description
| ------ | -----------
| ok     | no error
| ResourceNotAvailable      | cluster has not enough resources to fullfil your request at this time
| SandboxNoLongerAlive      | the sandbox has already finished its execution
| PermissionDenied          | you are not permitted to access this object
| MalformedRequest          | your request doesn't make sense
| NotEnoughMemoryRequested  | sandbox of this type needs more memory than you have requested
