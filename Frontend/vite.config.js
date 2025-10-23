import { execFile } from "node:child_process";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

/** @type {import("vite").Plugin */
const backend = {
  name: "backend",
  configureServer(server) {
    server.middlewares.use("/api", (req, res) => {
      const options = {
        cwd: "../Backend",
        encoding: "buffer"
      };
      const proc = execFile("python3", ["main.py", req.method, req.url], options, (error, stdout, stderr) => {
        if (error) {
          res.socket.write("HTTP/1.1 500 Internal Server Error\r\ncontent-type: text/plain\r\n\r\n");
          res.socket.end(stderr);
          process.stderr.write(`${req.method} ${req.url}\n`);
          process.stderr.write(stderr);
        } else {
          res.socket.end(stdout);
          process.stderr.write(stderr);
        }
      });
      req.pipe(proc.stdin);
    });
  }
};

/** @type {import("vite").UserConfig */
export default {
  plugins: [react(), tailwindcss(), backend],
  build: {
    modulePreload: {
      polyfill: false
    }
  }
};
