## Authorization

Login using HTTP basic auth. Use account name as login and API key as password.

## REST API

### POST /sandbox/

#### Input

| -------- | ------------ |
| owner    | target owner user (default: `me`) |
| memory   | memory allocation for sandbox (in MB) |
| timeout  | timeout in seconds |
| template | template ID or name | 

#### Output



### GET /template/

List templates.

#### Output

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

```json
{"status": "ok", "id": 431, "name": "template-name", "public": false}
```

### POST /template/:id

Change template.

#### Input

| ------ | ------- |
| public | boolean |
| name   | string  |

#### Output

```json
{"status": "ok"}
```

