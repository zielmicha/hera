## Authorization

Login using HTTP basic auth. Use account name as login and API key as password.

## REST API

### POST /sandbox/

#### Input

| name     | description
| -------- | ------------ |
| owner    | target owner user (default: `me`) |
| memory   | memory allocation for sandbox (in MB) |
| timeout  | timeout in seconds |
| template | template ID or name | 

#### Example query

```
POST /template/5

owner=me&memory=256&timeout=100&template=debian8
```
→
```json
{"status": "ok", "id": "e0f6f2bc-40db-476e-bd58-3b21ba36fab4"}
```


### GET /template/

List templates.

#### Example query

```
GET /template/
```
→
```json
{
    "status": "ok",
    "templates": [
        {"id": 431, "name": "template-name", "public": false}
    ]
}
```

### GET /template/:id

Get template info.

#### Example query

```
GET /template/5
```
→
```json
{"status": "ok", "id": 431, "name": "template-name", "public": false}
```

### POST /template/:id

Change template.

#### Input

| name   | description | example
| ------ | ----------- | --------
| public | boolean     | false
| name   | string      | debian8

#### Example query

```
POST /template/5

public=false&name=my-new-name
```
→
```json
{"status": "ok"}
```

