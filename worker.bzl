def _impl(ctx):
    args = [ctx.outputs.out.path] + [f.path for f in ctx.files.chunks]

    args_file = ctx.actions.declare_file(ctx.label.name + ".args")
    ctx.actions.write(
        output = args_file,
        content = "\n".join(args),
    )

    ctx.actions.run(
        mnemonic = "Concat",
        inputs = ctx.files.chunks + [args_file],
        outputs = [ctx.outputs.out],
        arguments = ["@" + args_file.path],
        executable = ctx.executable.merge_tool,
        execution_requirements = {
            "supports-workers": "1",
            "requires-worker-protocol": "json",
        },
    )

concat = rule(
    implementation = _impl,
    attrs = {
        "chunks": attr.label_list(allow_files = True),
        "out": attr.output(mandatory = True),
        "merge_tool": attr.label(
            executable = True,
            cfg = "exec",
            allow_files = True,
            default = Label("//:persistent_worker"),
        ),
    },
)
