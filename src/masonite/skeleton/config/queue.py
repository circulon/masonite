from masonite.environment import env

DRIVERS = {
    "default": env("QUEUE_DRIVER", "async"),
    "database": {
        "connection": "sqlite",
        "table": "jobs",
        "failed_table": "failed_jobs",
        "attempts": 3,
        "poll": 5,
        "tz": "UTC",
    },
    "amqp": {
        "username": env("QUEUE_USERNAME", "guest"),
        "password": env("QUEUE_PASSWORD", "guest"),
        "port": env("QUEUE_PORT", "5672"),
        "vhost": env("QUEUE_VHOST", ""),
        "host": env("QUEUE_HOST", "localhost"),
        # See https://pika.readthedocs.io/en/stable/modules/parameters.html#pika.connection.URLParameters
        # for valid connection options values
        "connection_options": {},
        "exchange": "",
        "channel": env("QUEUE_CHANNEL", "default"),
        "queue": "masonite",
        "tz": "UTC",
    },
    "async": {
        "blocking": False,
        "callback": "handle",
        "mode": "threading",
        "workers": 1,
    },
}
