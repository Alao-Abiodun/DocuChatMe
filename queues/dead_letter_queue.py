from bullmq import Queue

from queues.connection_queue import REDIS_URL

dead_letter_queue = Queue("dead-letter", {"connection": REDIS_URL})