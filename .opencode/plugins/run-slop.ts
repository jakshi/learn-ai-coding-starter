import { Plugin } from "@opencode/plugin";

export default Plugin.define({
  id: "sloperator.run-slop",
  setup: async (ctx) => {
    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description: "Run a SlopLang file and return stdout, stderr, and exitCode as JSON.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "File path, absolute or relative to the project root.",
              minLength: 1,
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input, context) => {
          const { path } = input as { path: string };
          const subprocess = Bun.spawn(["uv", "run", "--no-active", "sloperator.py", path], {
            cwd: ctx.location.project.directory,
            stdin: "ignore",
            stdout: "pipe",
            stderr: "pipe",
            signal: context.signal,
          });
          const [stdout, stderr, exitCode] = await Promise.all([
            new Response(subprocess.stdout).text(),
            new Response(subprocess.stderr).text(),
            subprocess.exited,
          ]);
          return { content: JSON.stringify({ stdout, stderr, exitCode }) };
        },
      });
    });
  },
});
