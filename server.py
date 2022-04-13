import os
import asyncio
import aiofiles
import optparse


def parse_args():
    usage = """usage: %prog [options] poetry-file"""

    parser = optparse.OptionParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_option("--port", type="int", help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_option("--iface", help=help, default="localhost")

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("Provide exactly one poetry file.")

    poetry_file = args[0]

    if not os.path.exists(args[0]):
        parser.error("No such file: %s" % poetry_file)

    return options, poetry_file


async def serve_poem(reader, writer, filename: str) -> None:
    task_number = await reader.read(100)
    task_number = task_number.decode()
    address = writer.get_extra_info("peername")
    print(f"{address} with task number {task_number} wants poetry")

    async with aiofiles.open(filename, mode="r") as f:
        data = await f.read()

    poem = data.encode()
    writer.write(poem)
    await writer.drain()

    print("Close the connection")
    writer.close()


async def main():
    options, poetry_file = parse_args()

    server = await asyncio.start_server(
        lambda r, w: serve_poem(r, w, poetry_file), options.iface, options.port
    )

    address = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {address}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
