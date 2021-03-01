async def auto_page_coro(coro, *args, **kwargs):
    '''
    Auto-pages coroutines that return a list

        coro, coroutine method
        Coroutine to page, must return a list

        *args, any
        Args to pass to coro

        **kwargs, any
        Kwargs to pass to coro
    '''

    objs = []
    kwargs["offset"] = 0
    kwargs["n"] = 100
    while True:
        response = await coro(*args, **kwargs)

        objs += response
        kwargs["offset"] += 100

        if len(response) < 100:
            break

    return objs
