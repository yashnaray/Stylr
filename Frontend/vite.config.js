import { execFile } from "node:child_process";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

/** @type {import("vite").ServerHook} */
function configureServer(server) {
  execFile("python3", ["init.py"], {
    cwd: "../Backend",
    stdio: "inherit"
  });
  server.middlewares.use("/api", (req, res) => {
    const options = {
      cwd: "../Backend",
      encoding: "buffer"
    };
    const args = ["main.py", req.method, req.url];
    const proc = execFile("python3", args, options, (error, stdout, stderr) => {
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

/** @type {import("vite").Plugin */
const backend = {
  name: "backend",
  configureServer
};

/** @type {import("vite").UserConfig */
export default {
  plugins: [react(), tailwindcss(), backend],
  build: {
    modulePreload: {
      polyfill: false
    }
  },
  clearScreen: false,
  define: {
    __api: JSON.stringify(process.env.STYLR_API_URL || "/api")
  }
};
