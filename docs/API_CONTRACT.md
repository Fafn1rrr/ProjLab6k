# ProjLab6k API Contract

This document defines the REST API contract used for communication between the frontend and backend of ProjLab6k.

## General rules

Base path:

```text
/api
```

Request and response bodies use JSON.

Frontend-facing field names use `camelCase`.

Example:

```json
{
  "profitPerUnit": 5.5,
  "availableTime": 80
}
```

Database column names may use `snake_case` internally.

Example:

```text
profit_per_unit
available_time
```

All API errors use the following format:

```json
{
  "message": "Error description."
}
```

---

# Implementation status

| Endpoint | Status |
|---|---|
| `GET /api/health` | Implemented |
| `GET /api/books` | Implemented |
| `POST /api/books` | Implemented |
| `PUT /api/books/{id}` | Implemented |
| `GET /api/machines` | Implemented |
| `POST /api/machines` | Implemented |
| `PUT /api/machines/{id}` | Implemented |
| `GET /api/orders` | Implemented |
| `POST /api/orders` | Implemented |
| `GET /api/processing-times` | Placeholder |
| `PUT /api/processing-times` | To implement |
| `POST /api/optimize` | To implement |

---

# Health

## GET `/api/health`

Checks whether the backend and database connection are available.

### Response — `200 OK`

```json
{
  "status": "ok"
}
```

### Possible errors

`503 Service Unavailable`

```json
{
  "message": "Database configuration error."
}
```

---

# Books

Book object:

```json
{
  "id": 1,
  "name": "Book A",
  "profitPerUnit": 5.5
}
```

Fields:

| Field | Type | Description |
|---|---|---|
| `id` | integer | Book identifier |
| `name` | string | Book name |
| `profitPerUnit` | number | Profit earned per produced unit |

## GET `/api/books`

Returns all books.

### Response — `200 OK`

```json
[
  {
    "id": 1,
    "name": "Book A",
    "profitPerUnit": 5.5
  },
  {
    "id": 2,
    "name": "Book B",
    "profitPerUnit": 8.0
  }
]
```

If no books exist:

```json
[]
```

---

## POST `/api/books`

Creates a new book.

### Request

```json
{
  "name": "Book A",
  "profitPerUnit": 5.5
}
```

### Validation

- `name` must be a string;
- `name` must contain at least 2 characters;
- `profitPerUnit` must be a number;
- `profitPerUnit` cannot be negative.

### Response — `201 Created`

```json
{
  "id": 1,
  "name": "Book A",
  "profitPerUnit": 5.5
}
```

### Possible errors

`400 Bad Request`

```json
{
  "message": "Book name must have at least 2 characters."
}
```

```json
{
  "message": "Profit per unit must be a number."
}
```

```json
{
  "message": "Profit per unit cannot be negative."
}
```

---

## PUT `/api/books/{id}`

Updates an existing book.

### Request

```json
{
  "name": "Updated Book",
  "profitPerUnit": 7.5
}
```

### Response — `200 OK`

```json
{
  "id": 1,
  "name": "Updated Book",
  "profitPerUnit": 7.5
}
```

### Possible errors

`400 Bad Request` — invalid input.

`404 Not Found`

```json
{
  "message": "Book not found."
}
```

---

# Machines

Machine object:

```json
{
  "id": 1,
  "name": "Printer 1",
  "availableTime": 80
}
```

Fields:

| Field | Type | Description |
|---|---|---|
| `id` | integer | Machine identifier |
| `name` | string | Machine name |
| `availableTime` | number | Available operating time |

## GET `/api/machines`

Returns all machines.

### Response — `200 OK`

```json
[
  {
    "id": 1,
    "name": "Printer 1",
    "availableTime": 80
  }
]
```

If no machines exist:

```json
[]
```

---

## POST `/api/machines`

Creates a new machine.

### Request

```json
{
  "name": "Printer 1",
  "availableTime": 80
}
```

### Validation

- `name` must be a string;
- `name` must contain at least 2 characters;
- `availableTime` must be a number;
- `availableTime` must be greater than `0`.

### Response — `201 Created`

```json
{
  "id": 1,
  "name": "Printer 1",
  "availableTime": 80
}
```

### Possible errors

`400 Bad Request`

```json
{
  "message": "Machine name must have at least 2 characters."
}
```

```json
{
  "message": "Available time must be a number."
}
```

```json
{
  "message": "Available time must be greater than 0."
}
```

---

## PUT `/api/machines/{id}`

Updates an existing machine.

### Request

```json
{
  "name": "Updated Printer",
  "availableTime": 100
}
```

### Response — `200 OK`

```json
{
  "id": 1,
  "name": "Updated Printer",
  "availableTime": 100
}
```

### Possible errors

`400 Bad Request` — invalid input.

`404 Not Found`

```json
{
  "message": "Machine not found."
}
```

---

# Orders

Order object:

```json
{
  "id": 1,
  "bookId": 2,
  "minQuantity": 100
}
```

Fields:

| Field | Type | Description |
|---|---|---|
| `id` | integer | Order identifier |
| `bookId` | integer | ID of the ordered book |
| `minQuantity` | integer | Minimum quantity that must be produced |

The referenced `bookId` must exist in `books`.

## GET `/api/orders`

Returns all orders.

### Response — `200 OK`

```json
[
  {
    "id": 1,
    "bookId": 2,
    "minQuantity": 100
  }
]
```

If no orders exist:

```json
[]
```

Results are ordered by `id`.

---

## POST `/api/orders`

Creates a new order.

### Request

```json
{
  "bookId": 2,
  "minQuantity": 100
}
```

### Validation

- `bookId` must be an integer (strings, booleans and decimals are rejected);
- referenced book must exist;
- `minQuantity` must be an integer (strings, booleans and decimals are rejected);
- `minQuantity` must be greater than `0`;
- `minQuantity` cannot exceed `2147483647` (PostgreSQL `INTEGER` limit).

### Response — `201 Created`

```json
{
  "id": 1,
  "bookId": 2,
  "minQuantity": 100
}
```

### Possible errors

`400 Bad Request`

```json
{
  "message": "Minimum quantity must be greater than 0."
}
```

Other `400 Bad Request` messages:

- `"Invalid JSON data."`
- `"Book ID must be an integer."`
- `"Minimum quantity must be an integer."`
- `"Minimum quantity is too large."`

`404 Not Found`

```json
{
  "message": "Book not found."
}
```

---

# Processing Times

A processing time defines how much machine time is required to produce one unit of a specific book on a specific machine.

Processing time object:

```json
{
  "bookId": 1,
  "machineId": 2,
  "time": 0.15
}
```

Fields:

| Field | Type | Description |
|---|---|---|
| `bookId` | integer | Book identifier |
| `machineId` | integer | Machine identifier |
| `time` | number | Processing time per unit |

The combination of `bookId` and `machineId` is unique.

## GET `/api/processing-times`

Returns all configured processing times.

### Response — `200 OK`

```json
[
  {
    "bookId": 1,
    "machineId": 1,
    "time": 0.15
  },
  {
    "bookId": 1,
    "machineId": 2,
    "time": 0.2
  }
]
```

If no processing times exist:

```json
[]
```

> Current implementation returns an empty array as a temporary placeholder.

---

## PUT `/api/processing-times`

Creates or updates the processing time for one book-machine pair.

The endpoint uses upsert behaviour:

- if the pair does not exist, it is created;
- if the pair already exists, its processing time is updated.

### Request

```json
{
  "bookId": 1,
  "machineId": 2,
  "time": 0.15
}
```

### Validation

- `bookId` must reference an existing book;
- `machineId` must reference an existing machine;
- `time` must be a number;
- `time` cannot be negative.

### Response — `200 OK`

```json
{
  "bookId": 1,
  "machineId": 2,
  "time": 0.15
}
```

### Possible errors

`400 Bad Request`

```json
{
  "message": "Processing time must be 0 or greater."
}
```

`404 Not Found`

```json
{
  "message": "Book not found."
}
```

or

```json
{
  "message": "Machine not found."
}
```

---

# Optimization

The optimization endpoint calculates an optimal printing plan using the information already stored in the database.

The frontend does not send books, machines, orders or processing times directly.

Backend flow:

```text
POST /api/optimize
        ↓
Load data from PostgreSQL
        ↓
Convert data to optimizer input
        ↓
Run PuLP/CBC optimizer
        ↓
Convert optimizer output to API response
        ↓
Return result to frontend
```

## POST `/api/optimize`

### Request

The current frontend sends an empty JSON object:

```json
{}
```

The backend loads required optimization data from PostgreSQL.

---

## Successful optimization

### Response — `200 OK`

```json
{
  "status": "optimal",
  "totalProfit": 1450.5,
  "items": [
    {
      "orderId": 1,
      "bookName": "Book A",
      "quantity": 120,
      "profit": 660.0
    },
    {
      "orderId": 2,
      "bookName": "Book B",
      "quantity": 100,
      "profit": 790.5
    }
  ],
  "machines": [
    {
      "machineName": "Printer 1",
      "used": 72,
      "available": 80,
      "remaining": 8
    },
    {
      "machineName": "Printer 2",
      "used": 45,
      "available": 60,
      "remaining": 15
    }
  ]
}
```

Fields:

### Root fields

| Field | Type | Description |
|---|---|---|
| `status` | string | Optimization status |
| `totalProfit` | number | Total profit of the calculated plan |
| `items` | array | Production plan |
| `machines` | array | Machine utilization information |

### Item fields

| Field | Type | Description |
|---|---|---|
| `orderId` | integer | Order identifier |
| `bookName` | string | Book name |
| `quantity` | integer | Quantity to produce |
| `profit` | number | Profit generated by this plan item |

### Machine fields

| Field | Type | Description |
|---|---|---|
| `machineName` | string | Machine name |
| `used` | number | Used machine time |
| `available` | number | Total available machine time |
| `remaining` | number | Remaining machine time |

---

## Infeasible optimization

If minimum quantities cannot be produced using the available machine time:

### Response — `200 OK`

```json
{
  "status": "infeasible",
  "message": "The minimum quantities cannot be met with the available machine time."
}
```

`infeasible` is returned as a valid optimization result rather than an HTTP error.

This allows the frontend to distinguish between:

- a correctly executed optimization with no feasible solution;
- an actual backend/API error.

---

## Invalid or missing input data

Examples:

- no orders exist;
- no machines exist;
- required processing times are missing;
- database data is invalid.

### Response — `400 Bad Request`

```json
{
  "message": "Required optimization data is missing."
}
```

---

# Common HTTP status codes

| Status | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | New resource created successfully |
| `400 Bad Request` | Invalid request or data |
| `404 Not Found` | Requested resource does not exist |
| `503 Service Unavailable` | Database/backend configuration problem |

---

# Current missing backend functionality

The following functionality is already expected by the frontend but is not yet implemented in the backend:

## Processing Times

```text
PUT /api/processing-times
```

`GET /api/processing-times` currently exists but returns only an empty array.

## Optimization

```text
POST /api/optimize
```

This endpoint still needs:

1. database data loading;
2. database-to-optimizer conversion;
3. PuLP/CBC execution;
4. optimizer result conversion;
5. optimal/infeasible result handling.

---

# Out of scope for the current contract

The following endpoints are not currently required by the existing frontend:

```text
DELETE /api/books/{id}
DELETE /api/machines/{id}
DELETE /api/orders/{id}
PUT /api/orders/{id}
```

They may be added later if corresponding functionality is introduced.

When a new API operation is introduced, this document must be updated before or together with its implementation.