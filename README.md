# Stylr

> Find your next fashion statement.

## Introduction

Stylr is a class project application that suggests clothing items to users
based on user-specified preferences. It is a simple web application based on
[React](https://react.dev) and
[React Router](https://reactrouter.com),
with a backend implemented in Python.

## Getting Started

### Frontend

You will need:

- A recent enough [Node](https://nodejs.org) (at least 20 or 22)
- [pnpm](https://pnpm.io)

Change to the `Frontend` directory, then:

```
pnpm install
pnpm dev
```

This will open the Vite server at the standard <http://localhost:5173>.
By default, the `/api` route will be proxied to <http://localhost:3031>.
This can be changed by setting the environment variable `STYLR_API_URL`.

### Backend

You will need:

- A recent enough [Python](https://www.python.org)

Change to the `Backend` directory, then:

```
./main.py
```

This will bind to port 3031 by default.
All routes are available at both the top level and `/api`.

## Rationale

### pnpm

For the frontend, we use [pnpm](https://pnpm.io). Compared to npm and Yarn,
pnpm shares package files between all projects using hardlinks and symlinks,
allowing for significant space savings.

Other alternatives considered:

- Yarn PnP uses an on-disk format that has limited compatability and requires
  all programs to be run through Yarn.
- Bun is an entire JavaScript runtime, which we do not need.

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
