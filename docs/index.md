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
POST /template/5

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

| name   | description |
| ------ | -----------
| ok     | no error
