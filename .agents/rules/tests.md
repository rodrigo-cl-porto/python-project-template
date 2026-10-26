# Testing Rules

Rules for writing automated tests in this repository. They complement [`AGENTS.md`](../../AGENTS.md) and
[`code-standards.md`](code-standards.md), and every agent must follow them when writing or reviewing code.

## 1. Every piece of code must be covered by automated tests

**This rule is CRITICAL and must never be ignored.** No feature, bug fix or refactoring is complete until it is covered
by passing automated tests.

- **If a feature has no test code, write the tests for it before validating or changing it.**
- **When fixing a bug, first write a test that reproduces it (and fails)**, then fix the code.
- **Every test is written with Pytest**, at every level. Files are named `test_*.py` and functions `test_*`. Use
  fixtures, `parametrize` and plain `assert`. Never write `unittest.TestCase` classes; `unittest.mock` is allowed only
  as a library of test doubles.
- `pytest.toml` already adds `src` to the `pythonpath`, so import the package directly
  (`from my_awesome_project import ...`).

❌ Undesirable:

```python
import unittest


class TestMoney(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(Money(Decimal(10)) + Money(Decimal(5)), Money(Decimal(15)))
```

✅ Fixed:

```python
def test_money_addition_sums_the_amounts():
    total = Money(Decimal(10)) + Money(Decimal(5))

    assert total == Money(Decimal(15))
```

## 2. Keep the test coverage at 80% or more

**The total test coverage must be at least 80%.** It is measured by
[pytest-cov](https://pytest-cov.readthedocs.io) (branch coverage) and configured in `.coveragerc`
(`fail_under = 80`), so `uv run poe test` fails when the coverage drops below the threshold.

```bash
uv run poe test                           # All tests, failing below 80% coverage
uv run pytest --cov --cov-report=html     # Coverage report in htmlcov/index.html
```

Coverage is a floor, not a goal: a line executed by a test without meaningful assertions is not tested (see
[Self-validating](#self-validating)).

## 3. Focus the tests on what is most critical

Spend the testing effort where a failure hurts the business the most. Critical behaviors (money, security, data
integrity, the main user journeys) deserve every branch, edge case and error path covered, at more than one test level.
Simple, low-risk behaviors need only their main cases.

For example, a checkout is far more critical than registering a product category:

| Behavior                   | Criticality | Expected tests                                                                  |
| -------------------------- | ----------- | ------------------------------------------------------------------------------- |
| Checkout                   | High        | Totals, discounts, taxes, payment failures, retries, empty cart, stock, e2e flow |
| Product category registry  | Low         | Creating a valid category and rejecting a duplicate name                        |

## 4. Follow the FIRST principles

| Letter | Principle       | Relevance                                                       |
| ------ | --------------- | --------------------------------------------------------------- |
| **F**  | Fast            | **High**                                                        |
| **I**  | Independent     | **High**                                                        |
| **R**  | Repeatable      | **High**                                                        |
| **S**  | Self-validating | **High**                                                        |
| **T**  | Timely          | Low — may be ignored (see [Timely](#timely-optional))           |

Test doubles replace real dependencies to keep tests fast and repeatable. Thanks to the
[Ports and Adapters](../skills/architecture-standards/SKILL.md#ports-and-adapters) architecture, they are plugged into the use cases
through their constructors:

| Double    | What it does                                                                    |
| --------- | ------------------------------------------------------------------------------- |
| **Dummy** | Fills a parameter that the test does not use.                                   |
| **Stub**  | Returns predefined answers to the calls made during the test.                   |
| **Fake**  | Has a working but simplified implementation (e.g. an in-memory repository).     |
| **Mock**  | Is pre-programmed with expectations and verifies the calls it receives.         |
| **Spy**   | Records the calls it receives, so the test can assert on them afterwards.       |

### Fast

Tests must run fast, so they can be run all the time. Replace slow dependencies (network, external APIs, databases,
sleeps) with stubs and fakes in unit tests; real infrastructure belongs only in integration and end-to-end tests.

❌ Undesirable — the unit test calls a real HTTP API, which is slow and may be unavailable:

```python
def test_convert_price_to_euros():
    convert_price = ConvertPrice(HttpExchangeRateProvider("https://api.exchange-rates.example"))

    converted = convert_price.execute(Money(Decimal(100)), "EUR")

    assert converted.currency == "EUR"
```

✅ Fixed — a stub implements the port and answers instantly:

```python
class StubExchangeRateProvider:
    def rate(self, source_currency: str, target_currency: str) -> Decimal:
        return Decimal("0.5")


def test_convert_price_applies_the_exchange_rate():
    convert_price = ConvertPrice(StubExchangeRateProvider())

    converted = convert_price.execute(Money(Decimal(100)), "EUR")

    assert converted == Money(Decimal(50), "EUR")
```

### Independent

Tests must not depend on each other nor on their execution order. If a test relies on the state left by another one,
a single failure breaks every test built on top of it, hiding the real cause. Create fresh state for each test with
fixtures and never share mutable state between tests.

❌ Undesirable — `test_pay_order` only passes if `test_add_order` runs first:

```python
repository = InMemoryOrderRepository()


def test_add_order():
    repository.add(Order(order_id="42"))

    assert repository.get("42") is not None


def test_pay_order():
    order = repository.get("42")
    order.add_line(OrderLine("book", Money(Decimal(10)), quantity=1))

    order.pay()

    assert order.status is OrderStatus.PAID
```

✅ Fixed — each test receives its own fresh objects from fixtures:

```python
@pytest.fixture
def draft_order() -> Order:
    return Order(order_id="42", lines=[OrderLine("book", Money(Decimal(10)), quantity=1)])


def test_added_order_can_be_retrieved(draft_order: Order):
    repository = InMemoryOrderRepository()

    repository.add(draft_order)

    assert repository.get("42") == draft_order


def test_paying_an_order_changes_its_status_to_paid(draft_order: Order):
    draft_order.pay()

    assert draft_order.status is OrderStatus.PAID
```

### Repeatable

Running a test many times, on any machine, at any date, must always give the same result. Never depend on the current
date or time, randomness, the network or external APIs that may answer differently on each call. Inject those values
(e.g. a `today` parameter or a clock port) and use mocks and stubs to control the answers of external services.

❌ Undesirable — `is_expired()` reads `date.today()`, so the test starts failing after November 30, 2026:

```python
def test_coupon_is_not_expired():
    coupon = Coupon(code="BLACKFRIDAY", expires_on=date(2026, 11, 30))

    assert not coupon.is_expired()
```

✅ Fixed — the date is injected, so the result never changes:

```python
def test_coupon_is_not_expired_before_its_expiration_date():
    coupon = Coupon(code="BLACKFRIDAY", expires_on=date(2026, 11, 30))

    is_expired = coupon.is_expired(today=date(2026, 11, 29))

    assert is_expired is False
```

✅ Fixed — a mock replaces the external payment API, returns a fixed receipt and verifies the call:

```python
from unittest.mock import create_autospec


def test_checkout_charges_the_cart_once(user: User, cart: Cart):
    payment_gateway = create_autospec(PaymentGateway, instance=True)
    payment_gateway.charge.return_value = Receipt(provider="stripe", attempt=1, latency_ms=120)
    checkout = Checkout(cart_repository=InMemoryCartRepository([cart]), payment_gateway=payment_gateway)

    checkout.execute(user, cart_id=cart.cart_id)

    payment_gateway.charge.assert_called_once_with(cart)
```

### Self-validating

A test must decide on its own whether it passed or failed, and **it must fail whenever the behavior breaks**. Coverage
alone proves nothing: validate the inputs, the returned values, the state changes, the interactions and the raised
exceptions with precise assertions. To check a test, break the code on purpose and confirm that the test fails.

❌ Undesirable — the test executes the code but would pass with almost any implementation:

```python
def test_apply_discount():
    total = apply_discount(Order(order_id="42", total=100.0), Coupon(rate=0.1, is_expired=False))

    assert total is not None
```

✅ Fixed — exact expected values for every relevant case, including the error path:

```python
@pytest.mark.parametrize(
    ("coupon", "expected_total"),
    [
        (None, 100.0),
        (Coupon(rate=0.1, is_expired=False), 90.0),
        (Coupon(rate=0.1, is_expired=True), 100.0),
    ],
)
def test_apply_discount_returns_the_expected_total(coupon: Coupon | None, expected_total: float):
    order = Order(order_id="42", total=100.0)

    total = apply_discount(order, coupon)

    assert total == pytest.approx(expected_total)


def test_apply_discount_rejects_a_missing_order():
    with pytest.raises(ValueError, match="Order is required"):
        apply_discount(None, coupon=None)
```

### Timely (optional)

Timely means imagining how the code and its API are expected to behave, and writing the tests for it, before
implementing the function, method or class (as in TDD). **This principle may be ignored**: tests may be written in
whatever order is most efficient for the LLM, as long as the behavior is fully covered before the task is finished.

## 5. Structure each test with Arrange/Act/Assert (AAA)

Every test has three phases, in this order:

| AAA         | What happens                                         |
| ----------- | ---------------------------------------------------- |
| **Arrange** | Build the objects and the state the test needs.      |
| **Act**     | Execute the single behavior under test.              |
| **Assert**  | Verify the result, the state changes or the calls.   |

- Separate the phases with a single blank line. In test functions this is the only exception to the
  [no blank lines rule](code-standards.md#10-avoid-blank-lines-inside-function-and-method-bodies); do not label the
  phases with comments.
- Test one behavior per test, with a single Act phase.
- Name the test after the behavior and its expected outcome, e.g. `test_paying_an_empty_order_is_rejected`.

❌ Undesirable — phases are interleaved and several behaviors are tested at once:

```python
def test_order():
    order = Order(order_id="42")
    with pytest.raises(EmptyOrderError):
        order.pay()
    order.add_line(OrderLine("book", Money(Decimal(10)), quantity=2))
    assert order.total == Money(Decimal(20))
    order.pay()
    assert order.status is OrderStatus.PAID
```

✅ Fixed — one behavior per test, with clear Arrange/Act/Assert phases:

```python
def test_paying_an_empty_order_is_rejected():
    order = Order(order_id="42")

    with pytest.raises(EmptyOrderError, match="Cannot pay empty order 42"):
        order.pay()

    assert order.status is OrderStatus.DRAFT


def test_order_total_sums_the_line_subtotals():
    order = Order(order_id="42")

    order.add_line(OrderLine("book", Money(Decimal(10)), quantity=2))

    assert order.total == Money(Decimal(20))
```

## 6. Follow the test pyramid

Have a wide base of unit tests, a middle layer of integration tests and a small top of end-to-end tests covering only
the critical user journeys. Each level lives in its own folder inside `tests/`:

```text
tests/
├── unit/          # Many tests: fast, isolated, no I/O
├── integration/   # Fewer tests: adapters against real infrastructure
└── e2e/           # Few tests: critical user journeys through the real entry points
```

| Level           | Folder               | What it verifies                                                                                        | Speed  |
| --------------- | -------------------- | ------------------------------------------------------------------------------------------------------- | ------ |
| **Unit**        | `tests/unit/`        | Domain and use cases in isolation, using test doubles for ports. No I/O.                                | Fast   |
| **Integration** | `tests/integration/` | Adapters against real infrastructure (database, file system, HTTP), use cases wired with real adapters. | Medium |
| **End-to-end**  | `tests/e2e/`         | The whole system from the user's point of view, through its real entry points (UI, API, CLI).           | Slow   |

### Unit test example

`tests/unit/test_money.py`:

```python
from decimal import Decimal

import pytest

from my_awesome_project.domain.exceptions import InvalidMoneyError
from my_awesome_project.domain.money import Money


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        (Decimal(10), Decimal(5), Decimal(15)),
        (Decimal(0), Decimal(0), Decimal(0)),
    ],
)
def test_money_addition_sums_the_amounts(first: Decimal, second: Decimal, expected: Decimal):
    total = Money(first) + Money(second)

    assert total == Money(expected)


def test_money_rejects_a_negative_amount():
    with pytest.raises(InvalidMoneyError, match="cannot be negative"):
        Money(Decimal(-1))
```

### Integration test example

`tests/integration/test_sqlite_order_repository.py`:

```python
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from my_awesome_project.adapters.outbound.sqlite_order_repository import SqliteOrderRepository
from my_awesome_project.domain.order import Order


@pytest.fixture
def connection(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(tmp_path / "test.db")
    connection.execute("CREATE TABLE orders (id TEXT PRIMARY KEY, total REAL)")
    yield connection
    connection.close()


def test_saved_order_can_be_retrieved(connection: sqlite3.Connection):
    repository = SqliteOrderRepository(connection)

    repository.add(Order(order_id="42", total=100.0))

    assert repository.get("42") == Order(order_id="42", total=100.0)
```

### End-to-end test example (Playwright)

End-to-end tests are preferably implemented with **[Playwright](https://playwright.dev/python/)** through the
`pytest-playwright` plugin, which provides the `page` fixture to Pytest. Install it with
`uv add --group dev pytest-playwright` and the browsers with `uv run playwright install`.

`tests/e2e/test_checkout.py`:

```python
import re

from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"


def test_user_can_complete_checkout(page: Page):
    page.goto(f"{BASE_URL}/products")
    page.get_by_role("button", name="Add to cart").first.click()
    page.get_by_role("link", name="Cart").click()

    page.get_by_role("button", name="Checkout").click()

    expect(page).to_have_url(re.compile(r".*/orders/\w+"))
    expect(page.get_by_text("Order placed successfully")).to_be_visible()
```

Prefer user-facing locators (`get_by_role`, `get_by_label`, `get_by_text`) over CSS/XPath selectors, and Playwright's
auto-waiting `expect` assertions over manual sleeps.

## 7. Running the tests

```bash
uv run pytest tests             # All tests
uv run pytest tests/unit        # Unit tests only
uv run pytest tests/integration # Integration tests only
uv run pytest tests/e2e         # End-to-end tests only
uv run poe test                 # All tests with coverage, stopping at the first failure
```
