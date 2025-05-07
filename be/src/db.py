import os

from ccc_logger import logger
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise


def init_db(app: FastAPI):
    logger.info("Initializing tortise database connection")
    register_tortoise(
        app,
        generate_schemas=True,  # Use False in production and do migrations with Aerich
        add_exception_handlers=True,
        config={
            "connections": {
                "default": os.environ["POSTGRES_DB_URL"],
            },
            "apps": {
                "models": {
                    "models": [
                        "models",
                    ],
                    "default_connection": "default",
                }
            },
        },
    )
