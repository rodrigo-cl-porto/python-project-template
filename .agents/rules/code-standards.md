# Code Standards

Coding conventions and Clean Code rules for this repository. They complement [`AGENTS.md`](../../AGENTS.md), and
every agent must follow them when writing or reviewing Python code.

## Code conventions

- Write code compatible with Python 3.13+ and use modern syntax (`list[int]`, `X | None`, `type` aliases, etc.).
- **Annotate types** on every function and method in `src/` (the package is typed — `py.typed`).
- Write **Google-style docstrings**; they feed the documentation through `mkdocstrings`.
- Follow the configured Ruff rules; do not disable rules without a justified need.

## Clean Code

Every rule below shows an undesirable example (❌) and how to fix it (✅).

### 1. Avoid magic numbers and magic strings

Unnamed literals hide intent and must be changed in many places. Give them a name with `Final`, an `Enum` or a
configuration value.

❌ Undesirable:

```python
def calculate_shipping(weight: float) -> float:
    if weight > 30:
        return weight * 2.5 + 15
    return weight * 2.5
```

✅ Fixed:

```python
from typing import Final

HEAVY_PACKAGE_THRESHOLD_KG: Final = 30
PRICE_PER_KG: Final = 2.5
HEAVY_PACKAGE_SURCHARGE: Final = 15


def calculate_shipping(weight_kg: float) -> float:
    base_price = weight_kg * PRICE_PER_KG
    if weight_kg > HEAVY_PACKAGE_THRESHOLD_KG:
        return base_price + HEAVY_PACKAGE_SURCHARGE
    return base_price
```

For a closed set of values, prefer an `Enum` over loose strings:

❌ Undesirable:

```python
if order.status == "shipped":
    ...
```

✅ Fixed:

```python
from enum import StrEnum


class OrderStatus(StrEnum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


if order.status is OrderStatus.SHIPPED:
    ...
```

### 2. Use meaningful, intention-revealing names

A name must tell what a variable holds, what a function does or what a class represents, without needing a comment.
Use `snake_case` for variables and functions, `PascalCase` for classes and `UPPER_SNAKE_CASE` for constants. Functions
are verbs (`calculate_total`), booleans are questions (`is_active`, `has_permission`), classes are nouns (`Invoice`).

❌ Undesirable:

```python
def proc(l: list[dict]) -> float:
    t = 0
    for x in l:
        if x["a"]:
            t += x["p"] * x["q"]
    return t
```

✅ Fixed:

```python
def calculate_active_items_total(items: list[OrderItem]) -> float:
    return sum(item.unit_price * item.quantity for item in items if item.is_active)
```

### 3. Keep functions small and focused (Single Responsibility)

A function should do one thing, at one level of abstraction. **Functions and methods must have at most 30 lines**
(docstring not included). When a behavior needs more than that, split it into smaller functions or methods. A function
that needs comments or blank lines to separate "sections" is also doing too much and must be split.

❌ Undesirable:

```python
def register_user(data: dict[str, str]) -> None:
    # validate
    if "@" not in data["email"]:
        msg = "Invalid email"
        raise ValueError(msg)
    if len(data["password"]) < 8:
        msg = "Password too short"
        raise ValueError(msg)
    # save
    connection = sqlite3.connect("app.db")
    connection.execute("INSERT INTO users VALUES (?, ?)", (data["email"], data["password"]))
    connection.commit()
    # notify
    smtp = smtplib.SMTP("smtp.mail.com")
    smtp.sendmail("noreply@mail.com", data["email"], "Welcome!")
```

✅ Fixed:

```python
def register_user(email: str, password: str) -> None:
    validate_email(email)
    validate_password(password)
    user = User(email=email, password_hash=hash_password(password))
    user_repository.add(user)
    notifier.send_welcome_message(user)


def validate_email(email: str) -> None:
    if "@" not in email:
        msg = f"Invalid email: {email}"
        raise InvalidEmailError(msg)


def validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        msg = f"Password must have at least {MIN_PASSWORD_LENGTH} characters"
        raise WeakPasswordError(msg)
```

### 4. Prefer guard clauses (early return) over nested or large if-else

Handle invalid and edge cases first and leave the function early. The "happy path" stays at the lowest indentation
level and is easy to read.

❌ Undesirable:

```python
def apply_discount(order: Order | None, coupon: Coupon | None) -> float:
    if order is not None:
        if order.items:
            if coupon is not None:
                if not coupon.is_expired:
                    return order.total * (1 - coupon.rate)
                else:
                    return order.total
            else:
                return order.total
        else:
            return 0.0
    else:
        msg = "Order is required"
        raise ValueError(msg)
```

✅ Fixed:

```python
def apply_discount(order: Order | None, coupon: Coupon | None) -> float:
    if order is None:
        msg = "Order is required"
        raise ValueError(msg)
    if not order.items:
        return 0.0
    if coupon is None or coupon.is_expired:
        return order.total
    return order.total * (1 - coupon.rate)
```

Long `if`/`elif` chains that dispatch on a value can often be replaced by a mapping or by `match`:

❌ Undesirable:

```python
def get_tax_rate(state: str) -> float:
    if state == "SP":
        return 0.18
    elif state == "RJ":
        return 0.20
    elif state == "MG":
        return 0.18
    else:
        msg = f"Unknown state: {state}"
        raise ValueError(msg)
```

✅ Fixed:

```python
TAX_RATE_BY_STATE: Final[dict[str, float]] = {"SP": 0.18, "RJ": 0.20, "MG": 0.18}


def get_tax_rate(state: str) -> float:
    if state not in TAX_RATE_BY_STATE:
        msg = f"Unknown state: {state}"
        raise UnknownStateError(msg)
    return TAX_RATE_BY_STATE[state]
```

Prefer to avoid the `break` and `continue` keywords in loops and in the conditionals inside them. They jump out of the
natural top-to-bottom flow, so the reader must track every exit point to know when the loop ends or which items it
processes. Express the intent directly instead: filter with a comprehension or generator, search with `next()`,
`any()` or `all()`, or extract the loop into a function and `return` from it.

❌ Undesirable:

```python
def find_first_overdue_invoice(invoices: list[Invoice], today: date) -> Invoice | None:
    overdue_invoice = None
    for invoice in invoices:
        if invoice.is_paid:
            continue
        if invoice.due_date < today:
            overdue_invoice = invoice
            break
    return overdue_invoice
```

✅ Fixed:

```python
def find_first_overdue_invoice(invoices: list[Invoice], today: date) -> Invoice | None:
    return next((invoice for invoice in invoices if invoice.is_overdue(today)), None)
```

Also avoid tautological conditions such as `if True:` and `while True:`. A condition that is always true hides the real
rule that controls the flow, which ends up buried in a `break` somewhere in the body. Write the actual condition in the
`while` statement (the walrus operator `:=` helps when the value must be read before it is checked), and remove
`if True:` blocks altogether.

❌ Undesirable:

```python
def read_commands(reader: CommandReader) -> list[Command]:
    commands = []
    while True:
        line = reader.read_line()
        if line == EXIT_COMMAND:
            break
        commands.append(parse_command(line))
    return commands
```

✅ Fixed:

```python
def read_commands(reader: CommandReader) -> list[Command]:
    commands = []
    while (line := reader.read_line()) != EXIT_COMMAND:
        commands.append(parse_command(line))
    return commands
```

### 5. Prefer classes to group related logic and state

When several functions operate on the same data, or pass the same arguments around, group them in a class. Use
`dataclasses` for data-centric objects.

❌ Undesirable:

```python
def deposit(balance: float, amount: float) -> float:
    return balance + amount


def withdraw(balance: float, amount: float) -> float:
    if amount > balance:
        msg = "Insufficient funds"
        raise ValueError(msg)
    return balance - amount


balance = 100.0
balance = deposit(balance, 50.0)
balance = withdraw(balance, 30.0)
```

✅ Fixed:

```python
from dataclasses import dataclass


@dataclass
class BankAccount:
    owner: str
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            msg = f"Insufficient funds to withdraw {amount}"
            raise InsufficientFundsError(msg)
        self.balance -= amount


account = BankAccount(owner="Alice", balance=100.0)
account.deposit(50.0)
account.withdraw(30.0)
```

### 6. Use specific exceptions instead of error codes or generic exceptions

Raise domain-specific exceptions and catch only what you can handle. Never silence errors with a bare `except`.

❌ Undesirable:

```python
def find_user(user_id: int) -> User | int:
    user = users.get(user_id)
    if user is None:
        return -1
    return user


try:
    process(find_user(42))
except Exception:
    pass
```

✅ Fixed:

```python
class UserNotFoundError(Exception):
    """Raised when a user does not exist."""


def find_user(user_id: int) -> User:
    user = users.get(user_id)
    if user is None:
        msg = f"User {user_id} not found"
        raise UserNotFoundError(msg)
    return user


try:
    process(find_user(42))
except UserNotFoundError:
    structlog.contextvars.bind_contextvars(user={"id": 42, "found": False}, outcome="skipped")
```

### 7. Don't Repeat Yourself (DRY)

Duplicated knowledge must be extracted into a single function, constant or class, so a change happens in one place.

❌ Undesirable:

```python
def price_for_member(price: float) -> float:
    return round(price * 0.9 * 1.18, 2)


def price_for_employee(price: float) -> float:
    return round(price * 0.7 * 1.18, 2)
```

✅ Fixed:

```python
TAX_RATE: Final = 0.18
MEMBER_DISCOUNT: Final = 0.10
EMPLOYEE_DISCOUNT: Final = 0.30


def final_price(price: float, discount_rate: float) -> float:
    discounted_price = price * (1 - discount_rate)
    return round(discounted_price * (1 + TAX_RATE), 2)


member_price = final_price(price, MEMBER_DISCOUNT)
employee_price = final_price(price, EMPLOYEE_DISCOUNT)
```

### 8. Do not write comments

Code must explain itself through intention-revealing names, small functions and type annotations. **Do not insert
comments**, unless they are absolutely necessary, such as explaining a complex regular expression or a workaround that
cannot be expressed in code. Never leave commented-out code (Ruff's `ERA` rule flags it). Docstrings are not comments:
keep Google-style docstrings on public APIs, since they feed the documentation.

❌ Undesirable:

```python
# increment the attempt counter
attempt += 1

# def old_calculation(x):
#     return x * 2

# check whether the user is allowed to buy alcohol
if user.age >= LEGAL_DRINKING_AGE and user.country in ALLOWED_COUNTRIES:
    ...
```

✅ Fixed:

```python
attempt += 1

if user.can_buy_alcohol():
    ...
```

✅ Acceptable exception — a complex regular expression, documented with `re.VERBOSE`:

```python
SEMANTIC_VERSION_PATTERN: Final = re.compile(
    r"""
    ^(?P<major>0|[1-9]\d*)
    \.(?P<minor>0|[1-9]\d*)
    \.(?P<patch>0|[1-9]\d*)
    (?:-(?P<prerelease>[0-9A-Za-z.-]+))?   # optional pre-release, e.g. -rc.1
    (?:\+(?P<build>[0-9A-Za-z.-]+))?$      # optional build metadata, e.g. +20260115
    """,
    re.VERBOSE,
)
```

### 9. Never write large files or classes

**A `.py` file (and therefore any class in it) must have at most 100 lines.** It is preferable to split the code into
several small, cohesive modules than to write one giant piece of logic in a single file. When a file approaches the
limit, extract classes, functions or value objects into their own modules.

❌ Undesirable:

```text
src/my_awesome_project/domain/
└── models.py          # 650 lines: Money, Order, OrderLine, Customer, Invoice...
```

✅ Fixed:

```text
src/my_awesome_project/domain/
├── money.py
├── order.py
├── order_line.py
├── customer.py
└── invoice.py
```

### 10. Avoid blank lines inside function and method bodies

A blank line inside the body of a function or method (docstrings excluded) usually separates two different steps, which
is a sign that the function does more than one thing and must be split. This also applies to test functions: their
Arrange/Act/Assert phases are not separated by blank lines
(see [`tests.md`](tests.md#5-structure-each-test-with-arrangeactassert-aaa)).

❌ Undesirable:

```python
def generate_invoice(order: Order) -> Invoice:
    subtotal = sum(line.subtotal for line in order.lines)
    discount = subtotal * order.customer.discount_rate

    tax = (subtotal - discount) * TAX_RATE
    shipping = calculate_shipping(order.weight_kg)

    total = subtotal - discount + tax + shipping
    return Invoice(order_id=order.order_id, total=total)
```

✅ Fixed:

```python
def generate_invoice(order: Order) -> Invoice:
    net_amount = calculate_net_amount(order)
    total = net_amount * (1 + TAX_RATE) + calculate_shipping(order.weight_kg)
    return Invoice(order_id=order.order_id, total=total)


def calculate_net_amount(order: Order) -> float:
    subtotal = sum(line.subtotal for line in order.lines)
    return subtotal * (1 - order.customer.discount_rate)
```

### 11. Avoid functions and methods with more than 4 parameters

**Functions and methods must have at most 4 parameters** (`self` and `cls` are not counted). A long parameter list is a
sign that the function must be split, or that related parameters belong together in a parameter object, such as a
value object.

❌ Undesirable:

```python
def create_shipment(
    recipient_name: str,
    street: str,
    city: str,
    postal_code: str,
    country: str,
    weight_kg: float,
) -> Shipment: ...
```

✅ Fixed:

```python
@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
    country: str


def create_shipment(recipient_name: str, address: Address, weight_kg: float) -> Shipment: ...
```

### 12. Declare variables close to where they are used

Declare each variable immediately before its first use, not at the top of the function. This keeps related lines
together, makes the scope obvious and avoids computing values that an early return would discard.

❌ Undesirable:

```python
def send_report(report: Report, recipients: list[str]) -> None:
    subject = f"Report {report.report_id}"
    attachment = render_pdf(report)
    if not recipients:
        return
    validate_report(report)
    for recipient in recipients:
        mailer.send(recipient, subject, attachment)
```

✅ Fixed:

```python
def send_report(report: Report, recipients: list[str]) -> None:
    if not recipients:
        return
    validate_report(report)
    subject = f"Report {report.report_id}"
    attachment = render_pdf(report)
    for recipient in recipients:
        mailer.send(recipient, subject, attachment)
```

### 13. Never put sensitive data in the code

**Never hardcode sensitive data** such as API keys, tokens, passwords or connection strings in the code, in tests or in
configuration files under version control. Keep them in an external `.env` file (already listed in `.gitignore`) and
read them at runtime, for example with [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
(`uv add pydantic-settings`). Commit a `.env.example` file with the variable names and placeholder values only.

❌ Undesirable:

```python
PAYMENT_API_KEY = "sk-test-1234567890abcdef"

client = PaymentClient(api_key=PAYMENT_API_KEY)
```

✅ Fixed:

```dotenv
# .env (never versioned)
PAYMENT_API_KEY=<your-payment-api-key>
```

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    payment_api_key: SecretStr


settings = Settings()
client = PaymentClient(api_key=settings.payment_api_key.get_secret_value())
```
