from django.conf import settings

from core.redis import get_redis_client

LOCK_PREFIX = 'seat_lock'


def build_seat_lock_key(showtime_id: int, seat_id: int) -> str:
    return f'{LOCK_PREFIX}:{showtime_id}:{seat_id}'


def acquire_seat_lock(showtime_id: int, seat_id: int, user_id: int) -> bool:
    redis_client = get_redis_client()
    key = build_seat_lock_key(showtime_id, seat_id)

    return bool(
        redis_client.set(
            key,
            str(user_id),
            nx=True,
            ex=settings.SEAT_LOCK_TTL_SECONDS,
        )
    )


def get_seat_lock_owner(showtime_id: int, seat_id: int) -> str | None:
    redis_client = get_redis_client()
    key = build_seat_lock_key(showtime_id, seat_id)
    return redis_client.get(key)


def get_seat_lock_ttl(showtime_id: int, seat_id: int) -> int | None:
    redis_client = get_redis_client()
    key = build_seat_lock_key(showtime_id, seat_id)
    ttl = redis_client.ttl(key)

    if ttl is None or ttl < 0:
        return None

    return ttl


def release_seat_lock(showtime_id: int, seat_id: int, user_id: int) -> bool:
    redis_client = get_redis_client()
    key = build_seat_lock_key(showtime_id, seat_id)
    current_owner = redis_client.get(key)

    if current_owner != str(user_id):
        return False

    redis_client.delete(key)
    return True


def get_locked_seats(showtime_id: int) -> dict[int, str]:
    redis_client = get_redis_client()
    pattern = f'{LOCK_PREFIX}:{showtime_id}:*'
    locked_seats: dict[int, str] = {}

    for key in redis_client.scan_iter(match=pattern):
        owner = redis_client.get(key)
        if owner is None:
            continue

        seat_id = int(key.split(':')[-1])
        locked_seats[seat_id] = owner

    return locked_seats
