# Standard Input Hanger for Brython Runner

An implementation of *hanger* server for [Brython Runner](https://github.com/pythonpad/brython-runner).

To receive standard input from the Python code running in a web worker environment with Brython, Brython Runner uses a synchronous XHR to simulate the blocking `input()` function. 

This is how `input()` works in Brython Runner: 

1. When `input()` is called, Brython Runner instance in the web worker requests to **open** a data slot in the *hanger* server. Server reserves a space to store the data and returns a *token* for that space.
1. The instance in the web worker hands over the *token* to the browser's main thread. 
1. The instance in the web worker then makes a synchronous XHR to **read** the data from *hanger* server with the *token*. Since the data is not available yet, the *hanger* server holds the connection until it receives the requested data.
1. Meanwhile, Brython Runner instance in the main thread receives the *token* from the web worker instance. The main thread instance then calls the callback function (`options.stdin.readline()`) to collect the data from the user.
1. When the main thread instance collected the standard input data from the user, it requests to **write** the data in the *hanger* server with the *token*. 
1. Aha! Now the *hanger* server got the data, so it returns that data for the **read** request from the Brython Runner instance in the web worker that has been on hold for so long. 
1. `input()` function can now return the data received from the server.

## Installation

Set up a virtual environment and install dependencies:

```
$ python -m venv ./env
$ source ./env/bin/activate
(env) $ pip install -r requirements.txt
```

## Usage

Run server:

```
(env) $ python app.py
```

Run server with *host* and *port* options:

```
(env) $ python app.py 0.0.0.0:9095
```

## API

This server application serves a few simple functions. 

#### POST `/hanger/open/`

The server **opens** a data slot. Returns a *token* (a string value with length=16) as a plain text.

#### POST `/hanger/{token}/write/`

The server **writes** data to the requested slot according to the *token*. Returns the *token* as a plain text.

#### POST `/hanger/{token}/read/`

The server **reads** data from the requested slot according to the *token*. Returns the data as a plain text.

When the requested data slot does not exist, the server responds with 404.

When the requested data slot exists but there is no data written in the slot, the server holds the connection and waits until it receives the data for that slot. 
