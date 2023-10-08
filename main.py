import asyncio
import logging
import os
import random

import aredis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


async def connect_to_redis():
    try:
        redis_host = os.environ.get("REDIS", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        redis_password = os.environ.get("REDIS_PASSWORD", "")
        connection = aredis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=0,
            ssl=True,
        )
        logging.info("Connected to Redis")
        return connection
    except Exception as e:
        logging.error(f"Error connecting to Redis: {e}")
        raise


async def ping_redis(redis_connection):
    try:
        response = await redis_connection.ping()
        if response:
            logging.info("Ping successful. Redis is responsive.")
        else:
            logging.warning("Ping to Redis did not receive a proper response.")
    except Exception as e:
        logging.error(f"Error pinging Redis: {e}")


async def perform_random_action(redis_connection):
    actions = ["set", "get", "incr"]
    action = random.choice(actions)
    if action == "set":
        key = f"key_{random.randint(1, 100)}"
        value = f"value_{random.randint(1, 100)}"
        await redis_connection.set(key, value)
        logging.info(f"Set key '{key}' with value '{value}'")
    elif action == "get":
        key = f"key_{random.randint(1, 100)}"
        value = await redis_connection.get(key)
        logging.info(f"Got value '{value}' for key '{key}'")
    elif action == "incr":
        key = f"counter_{random.randint(1, 10)}"
        value = await redis_connection.incr(key)
        logging.info(f"Incremented counter '{key}', new value: {value}")


async def job(redis_connection):
    try:
        await perform_random_action(redis_connection)
    except Exception as e:
        logging.error(f"Error performing random action: {e}")


async def main():
    redis_connection = await connect_to_redis()
    await ping_redis(redis_connection)
    await job(redis_connection)

    while True:
        await job(redis_connection)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
