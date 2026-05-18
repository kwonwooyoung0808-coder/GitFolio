async def collect_stream(async_iterable) -> str:
    chunks = []
    async for chunk in async_iterable:
        chunks.append(chunk)
    return "".join(chunks)
