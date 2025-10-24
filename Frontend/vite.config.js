import { execFile, execFileSync, spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";

const databaseDirectory = "../Backend/postgres";

function initDatabase() {
  try {
    mkdirSync(databaseDirectory);
  } catch (e) {
    if (e.code === "EEXIST") {
      return; // database directory exists, we are done
    }
    throw e;
  }
  const args = ["-A", "trust", "-U", "stylr", "-D", databaseDirectory];
  execFileSync("initdb", args, { stdio: "inherit" });
}

/** @type {import("vite").ServerHook} */
function configureServer(server) {
  initDatabase();
  const postgres = spawn("postgres", ["-p", "3101", "-D", databaseDirectory], {
    stdio: ["ignore", "inherit", "inherit"]
  });
  server.httpServer.on("close", () => {
    postgres.kill("SIGINT");
  });
  process.on("SIGINT", () => {
    server.close();
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
  clearScreen: false
};
