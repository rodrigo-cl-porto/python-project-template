# Wide Event Logging Example

Complete example of the [wide event logging skill](../SKILL.md): one wide event per unit of work, with the execution date and time and the origin of the main event, enriched along the way, emitted once and appended to a `.jsonl` file.

## ❌ Undesirable

Many small, unstructured log lines without context:

```python
import logging

logger = logging.getLogger(__name__)


def checkout(user_id: str, cart_id: str) -> None:
    logger.info("Starting checkout")
    logger.info(f"Loading cart {cart_id}")
    cart = cart_repository.get(cart_id)
    logger.info("Processing payment")
    try:
        payment_gateway.charge(cart)
    except PaymentError:
        logger.error("Payment failed")
        raise
    logger.info("Checkout done")
```

## ✅ Fixed

### `adapters/code_origin.py`

```python
import inspect
from collections.abc import Callable
from pathlib import Path
from types import CodeType, TracebackType
from typing import Final

PACKAGE_ROOT: Final = Path(__file__).resolve().parents[1]


def code_of(unit_of_work: Callable[..., object]) -> CodeType:
    """Return the code of a function or method, unwrapping the decorators applied to it."""
    return inspect.unwrap(unit_of_work).__code__


def belongs_to_project(code: CodeType) -> bool:
    """Tell whether a piece of code lives inside the project package."""
    return Path(code.co_filename).resolve().is_relative_to(PACKAGE_ROOT)


def describe_code(code: CodeType) -> dict[str, str]:
    """Describe the file and the function or method where a piece of code lives."""
    file_path = Path(code.co_filename).resolve().relative_to(PACKAGE_ROOT.parent)
    return {"file": file_path.as_posix(), "function": code.co_qualname}


def find_raising_code(traceback: TracebackType | None, default: CodeType) -> CodeType:
    """Return the deepest project frame of a traceback, which is where the error was raised."""
    raising_code = default
    while traceback is not None:
        if belongs_to_project(traceback.tb_frame.f_code):
            raising_code = traceback.tb_frame.f_code
        traceback = traceback.tb_next
    return raising_code
```

### `adapters/observability.py`

`configure_logging` renders each event as a single JSON line and appends it to `logs/events.jsonl` at the repository root. The `logs/` folder is resolved from the location of this file (`src/my_awesome_project/adapters/observability.py`), never from the current working directory. The `events_file` parameter exists only so tests can redirect the events to `tmp_path`.

```python
import functools
import random
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from types import CodeType
from typing import Any, Final

import structlog

from my_awesome_project.adapters.code_origin import code_of, describe_code, find_raising_code

SERVICE_NAME: Final = "my-awesome-project"
SLOW_REQUEST_THRESHOLD_MS: Final = 2000
HAPPY_PATH_SAMPLE_RATE: Final = 0.05
MILLISECONDS_PER_SECOND: Final = 1000
REPOSITORY_ROOT: Final = Path(__file__).resolve().parents[3]
EVENTS_FILE: Final = REPOSITORY_ROOT / "logs" / "events.jsonl"
EVENTS_FILE_ENCODING: Final = "utf-8"

logger = structlog.get_logger()


def configure_logging(events_file: Path = EVENTS_FILE) -> None:
    """Configure structlog to append every wide event as one JSON line to `logs/events.jsonl`."""
    events_file.parent.mkdir(parents=True, exist_ok=True)
    events_stream = events_file.open("a", encoding=EVENTS_FILE_ENCODING)  # noqa: SIM115
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.WriteLoggerFactory(file=events_stream),
    )


def should_keep(event: dict[str, Any]) -> bool:
    """Tail sampling: decide whether to emit the event after it is complete."""
    if event.get("outcome") == "error":
        return True
    if event.get("duration_ms", 0) > SLOW_REQUEST_THRESHOLD_MS:
        return True
    if event.get("user", {}).get("subscription") == "enterprise":
        return True
    return random.random() < HAPPY_PATH_SAMPLE_RATE


def start_event(operation: str, context: dict[str, object]) -> None:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        operation=operation,
        request_id=str(uuid.uuid4()),
        service=SERVICE_NAME,
        version=version(SERVICE_NAME),
        timestamp=datetime.now(UTC).isoformat(timespec="milliseconds"),
        **context,
    )


def bind_failure(error: Exception, unit_of_work_code: CodeType) -> None:
    raising_code = find_raising_code(error.__traceback__, default=unit_of_work_code)
    structlog.contextvars.bind_contextvars(
        outcome="error",
        origin=describe_code(raising_code),
        error={"type": type(error).__name__, "message": str(error)},
    )


def emit_event(operation: str, start_time: float) -> None:
    duration_ms = round((time.perf_counter() - start_time) * MILLISECONDS_PER_SECOND, 2)
    structlog.contextvars.bind_contextvars(duration_ms=duration_ms)
    if should_keep(structlog.contextvars.get_contextvars()):
        logger.info(operation)
    structlog.contextvars.clear_contextvars()


def wide_event[**P, R](operation: str, **context: object) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Run the decorated unit of work and emit everything it collected as a single wide event."""

    def decorator(unit_of_work: Callable[P, R]) -> Callable[P, R]:
        unit_of_work_code = code_of(unit_of_work)

        @functools.wraps(unit_of_work)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start_event(operation, context)
            start_time = time.perf_counter()
            try:
                result = unit_of_work(*args, **kwargs)
            except Exception as error:
                bind_failure(error, unit_of_work_code)
                raise
            else:
                structlog.contextvars.bind_contextvars(outcome="success", origin=describe_code(unit_of_work_code))
                return result
            finally:
                emit_event(operation, start_time)

        return wrapper

    return decorator
```

### `bootstrap.py`

```python
def configure_application() -> None:
    configure_logging()
```

### `application/use_cases/checkout.py`

The use case enriches the current event, including the interaction with the external payment service:

```python
class Checkout:
    def execute(self, user: User, cart_id: str) -> None:
        cart = self._cart_repository.get(cart_id)
        structlog.contextvars.bind_contextvars(
            user={"id": user.user_id, "subscription": user.subscription},
            cart={"id": cart.cart_id, "item_count": len(cart.items), "total_cents": cart.total_cents},
        )
        receipt = self._payment_gateway.charge(cart)
        structlog.contextvars.bind_contextvars(
            payment={"provider": receipt.provider, "attempt": receipt.attempt, "latency_ms": receipt.latency_ms},
        )
```

### `adapters/inbound/cli.py`

```python
@wide_event("checkout", channel="cli")
def checkout_command(user: User, cart_id: str) -> None:
    build_checkout().execute(user, cart_id)
```

### `adapters/inbound/payment_webhook.py` (received external event)

```python
@wide_event("payment_webhook", channel="webhook", source="stripe")
def handle_payment_webhook(notification: PaymentNotification) -> None:
    structlog.contextvars.bind_contextvars(
        delivery_id=notification.delivery_id,
        payment={"status": notification.status},
    )
    build_confirm_payment().execute(notification.order_id)
```

### `tests/integration/test_observability.py`

```python
import json
from collections.abc import Iterator
from pathlib import Path

import pytest
import structlog

from my_awesome_project.adapters.observability import configure_logging, wide_event


class PaymentDeclinedError(Exception):
    pass


@pytest.fixture
def events_file(tmp_path: Path) -> Iterator[Path]:
    events_file = tmp_path / "logs" / "events.jsonl"
    configure_logging(events_file)
    yield events_file
    structlog.reset_defaults()


@wide_event("checkout", channel="test")
def failing_checkout() -> None:
    msg = "Card declined"
    raise PaymentDeclinedError(msg)


def test_failed_unit_of_work_appends_one_json_line_to_the_events_file(events_file: Path):
    with pytest.raises(PaymentDeclinedError):
        failing_checkout()
    events = [json.loads(line) for line in events_file.read_text(encoding="utf-8").splitlines()]
    assert len(events) == 1
    assert events[0]["outcome"] == "error"
    assert events[0]["error"] == {"type": "PaymentDeclinedError", "message": "Card declined"}
```

## Resulting `.jsonl` lines

Each event is a **single line** in `logs/events.jsonl`, at the repository root. They are shown formatted below only for readability.

On success, pointing to the unit of work:

```json
{
  "event": "checkout", "level": "info", "timestamp": "2026-01-15T10:23:44.365+00:00",
  "origin": {"file": "my_awesome_project/adapters/inbound/cli.py", "function": "checkout_command"},
  "operation": "checkout", "request_id": "8bf7ec2d-...", "service": "my-awesome-project", "version": "1.4.0",
  "channel": "cli", "outcome": "success", "duration_ms": 1247.31,
  "user": {"id": "user_456", "subscription": "premium"},
  "cart": {"id": "cart_xyz", "item_count": 3, "total_cents": 15999},
  "payment": {"provider": "stripe", "attempt": 1, "latency_ms": 1089}
}
```

On failure, pointing to the method that raised the error:

```json
{
  "event": "checkout", "level": "info", "timestamp": "2026-01-15T10:24:02.118+00:00",
  "origin": {
    "file": "my_awesome_project/adapters/outbound/payment_gateways/stripe_payment_gateway.py",
    "function": "StripePaymentGateway.charge"
  },
  "operation": "checkout", "request_id": "1c9e4a7b-...", "service": "my-awesome-project", "version": "1.4.0",
  "channel": "cli", "outcome": "error", "duration_ms": 312.08,
  "error": {"type": "PaymentDeclinedError", "message": "Card declined for cart cart_xyz"},
  "user": {"id": "user_456", "subscription": "premium"},
  "cart": {"id": "cart_xyz", "item_count": 3, "total_cents": 15999}
}
```

What the file actually contains (one event per line):

```jsonl
{"event": "checkout", "level": "info", "timestamp": "2026-01-15T10:23:44.365+00:00", "origin": {"file": "my_awesome_project/adapters/inbound/cli.py", "function": "checkout_command"}, "outcome": "success", "...": "..."}
{"event": "checkout", "level": "info", "timestamp": "2026-01-15T10:24:02.118+00:00", "origin": {"file": "my_awesome_project/adapters/outbound/payment_gateways/stripe_payment_gateway.py", "function": "StripePaymentGateway.charge"}, "outcome": "error", "...": "..."}
```
