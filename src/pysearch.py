import os
import io
import zlib
import re
import asyncio
import aiohttp

from tornado.platform.asyncio import AnyThreadEventLoopPolicy

asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


def parse_object_inv(stream, url):
    # key: URL
    # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
    result = {}

    # first line is version info
    inv_version = stream.readline().rstrip()

    if inv_version != "# Sphinx inventory version 2":
        raise RuntimeError("Invalid objects.inv file version.")

    # next line is "# Project: <name>"
    # then after that is "# Version: <version>"
    projname = stream.readline().rstrip()[11:]
    version = stream.readline().rstrip()[11:]

    # next line says if it's a zlib header
    line = stream.readline()
    if "zlib" not in line:
        raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

    # This code mostly comes from the Sphinx repository.
    entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
    for line in stream.read_compressed_lines():
        match = entry_regex.match(line.rstrip())
        if not match:
            continue

        name, directive, prio, location, dispname = match.groups()
        domain, _, subdirective = directive.partition(":")
        if directive == "py:module" and name in result:
            # From the Sphinx Repository:
            # due to a bug in 1.1 and below,
            # two inventory entries are created
            # for Python modules, and the first
            # one is correct
            continue

        # Most documentation pages have a label
        if directive == "std:doc":
            subdirective = "label"

        if location.endswith("$"):
            location = location[:-1] + name

        key = name if dispname == "-" else dispname
        prefix = f"{subdirective}:" if domain == "std" else ""

        if projname == "discord.py":
            key = key.replace("discord.ext.commands.", "").replace("discord.", "")

        result[f"{prefix}{key}"] = os.path.join(url, location)

    return result


def finder(text, collection, *, key=None, lazy=True):
    suggestions = []
    text = str(text)
    pat = ".*?".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]


async def read_inv(word):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://docs.python.org/ja/3/objects.inv") as resp:
            if resp.status != 200:
                raise RuntimeError("Cannot build rtfm lookup table, try again later.")

            # print(resp.read())
            stream = SphinxObjectFileReader(await resp.read())
            result = parse_object_inv(stream, "https://docs.python.org/ja/3")
            # print(result)

    matches = finder(word, result.items(), key=lambda t: t[0], lazy=False)[:8]

    return {key: url for key, url in matches}


def main(word):
    loop = asyncio.get_event_loop()
    matches = loop.run_until_complete(read_inv(word))
    loop.close()
    return matches
