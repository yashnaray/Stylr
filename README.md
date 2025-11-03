# Stylr

> Find your next fashion statement.

## Introduction

Stylr is a class project application that suggests clothing items to users
based on user-specified preferences. It is a simple web application based on
[React](https://react.dev) and
[React Router](https://reactrouter.com),
with a backend implemented in Python.

## Getting Started

You will need:

- A recent enough [Python](https://docs.python.org/3/) (at least 3.8)
- A recent enough [Node](https://nodejs.org/api/) (at least 20 or 22)
- [pnpm](https://pnpm.io) (recommended) or other package manager

Change to the `Frontend` directory, then:

```
pnpm install
pnpm dev
```

This will open the Vite server at the standard <http://localhost:5173>
and mount the backend at `/api`. This will also automatically
download the data for the backend and initialize a local testing database
if you haven't done so already. The backend uses
[SQLite](https://docs.python.org/3/library/sqlite3.html) by default,
so no additional database packages are needed during development.

## Rationale

### pnpm

For the frontend, we use [pnpm](https://pnpm.io). Compared to npm and Yarn,
pnpm shares package files between all projects using hardlinks and symlinks,
allowing for significant space savings.

Other alternatives considered:

- Yarn PnP uses an on-disk format that has limited compatability and requires
  all programs to be run through Yarn.
- Bun is an entire JavaScript runtime, which we do not need.

### CGI

The backend is a
[CGI](https://httpd.apache.org/docs/current/howto/cgi.html) application.
While CGI is horribly inefficient and is universally considered to be
a terrible way of doing things (see the documentation for the
[removed Python `cgi` module](https://docs.python.org/3/library/cgi.html)),
this does allow us to host the project on
[cise.ufl.edu](https://cise.ufl.edu)
and take advantage of the university database servers.
This has several benefits:

- This service is provided free to members of the University of Florida
  computer science department.
  This offer is hard to beat; free application hosting especially for Python is
  difficult to find, and free database hosting is virtually nonexistent.
- Having both our backend and database in the same network improves data
  locality and reduces database access latencies.
- As our application is expected to have few users (if any), we are more
  concerned about idle overhead than peak traffic throughput.
  With CGI, there is no persistent server process, so resource usage while idle
  is no more than that of a basic web server.
- In Python, it is very easy to cause the process to block.
  (Contrast this with Node.js, in which one has to _opt-out_ of the thread pool
  by using the `*Sync()` filesystem functions and network operations are
  _always_ asynchronous.)
  By forcing each request into a separate process, we ensure that they are
  handled concurrently and do not interfere with each other.
- Since it is difficult for processes to share state, the above point virtually
  forces the backend to be stateless, eliminating a number of potential bugs.
  (In contrast, sharing state between threads is all too easy to do and
  notoriously hard to do correctly.)

Also note the following points:

- Modern applications are increasingly offloading part or most of their work to
  "serverless functions," in which edge nodes can spin up server processes
  automatically when clients interact with the application, and terminate these
  processes to save resources when traffic is low.
  When one of these function instances is first initialized, it is known as a
  "cold start," and the performance for the request that triggered the
  initialization is no better than CGI.
  More information is available in the
  [Vercel documentation](https://vercel.com/docs/fundamentals/what-is-compute).

At any rate, if we were trying to make it efficient,
we wouldn't be writing it in Python anyway.

## Copyright

Copyright (c) 2025 Daniel Li, Yash Narayan, Sebastian Jurado, and Gavin Schroeder

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
