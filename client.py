import asyncio
import optparse


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ..."""

    parser = optparse.OptionParser(usage)

    _, addresses = parser.parse_args()

    if not addresses:
        print(parser.format_help())
        parser.exit()

    def parse_address(address):
        if ":" not in address:
            host = "127.0.0.1"
            port = address
        else:
            host, port = address.split(":", 1)

        if not port.isdigit():
            parser.error("Ports must be integers.")

        return host, int(port)

    return list(map(parse_address, addresses))


async def client(task_number: str, address: str, port: int) -> None:
    try:
        reader, writer = await asyncio.open_connection(address, port)
    except ConnectionRefusedError:
        print(f"Cannot connect to {address}:{port}")
        return

    task_number = task_number
    writer.write(task_number.encode())
    poem = ""
    while True:
        data = await reader.read(10)
        print(f"data from task {task_number}: ", data.decode())
        poem += data.decode()
        # await asyncio.sleep(0.1)
        if not data:
            break
    print(f"Close task {task_number} connection ")
    writer.close()
    print(poem)
    return


async def main():
    addresses = parse_args()
    await asyncio.gather(
        *[
            asyncio.create_task(client(str(i + 1), address[0], address[1]))
            for i, address in enumerate(addresses)
        ]
    )


if __name__ == "__main__":
    asyncio.run(main())
