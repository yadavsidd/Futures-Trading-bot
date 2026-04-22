import os
import time
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.live import Live
from rich.spinner import Spinner

from bot.logging_config import setup_logging
from bot.client import BinanceClient, APIError, NetworkError
from bot.orders import (
    place_market_order,
    place_limit_order,
    place_stop_limit_order,
    get_order,
    format_order_result,
)
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

console = Console()

BANNER = """
██████╗ ██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗███████╗
██╔══██╗██║████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝
██████╔╝██║██╔██╗ ██║███████║██╔██╗ ██║██║     █████╗  
██╔══██╗██║██║╚██╗██║██╔══██║██║╚██╗██║██║     ██╔══╝  
██████╔╝██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗███████╗
╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
         Futures Testnet Trading Bot  •  demo-fapi
"""

ORDER_TYPES = ["MARKET", "LIMIT", "STOP_LIMIT"]
SIDES = ["BUY", "SELL"]

def clear():
    os.system("clear")

def show_banner():
    clear()
    console.print(
        Panel(Align.center(Text(BANNER, style="bold cyan")),
              border_style="bright_cyan",
              padding=(0, 2)),
    )

def show_menu():
    console.print()
    menu = Table(show_header=False, box=box.ROUNDED, border_style="bright_blue", padding=(0, 2))
    menu.add_column(justify="center", style="bold white")
    menu.add_column(style="dim white")
    menu.add_row("[1]", "📈  Place Order")
    menu.add_row("[2]", "🔍  Check Order Status")
    menu.add_row("[3]", "📋  View Recent Logs")
    menu.add_row("[4]", "❌  Exit")
    console.print(Align.center(menu))
    console.print()

def prompt_validated(label: str, validator, optional=False, hint=""):
    while True:
        raw = Prompt.ask(f"  [bold cyan]{label}[/bold cyan]{(' [dim]' + hint + '[/dim]') if hint else ''}")
        if optional and raw.strip() == "":
            return None
        try:
            return validator(raw.strip())
        except ValueError as e:
            console.print(f"  [bold red]  ✘[/bold red] {e}")

def pick_from(label: str, choices: list) -> str:
    choices_str = " / ".join(f"[bold]{c}[/bold]" for c in choices)
    while True:
        raw = Prompt.ask(f"  [bold cyan]{label}[/bold cyan] ({choices_str})")
        val = raw.strip().upper()
        if val in choices:
            return val
        console.print(f"  [bold red]  ✘[/bold red] Must be one of: {', '.join(choices)}")

def with_spinner(message: str, fn):
    """Run fn() while showing a spinner."""
    result = [None]
    error = [None]
    with Live(Spinner("dots", text=f" [yellow]{message}[/yellow]"), console=console, refresh_per_second=12):
        try:
            result[0] = fn()
        except Exception as e:
            error[0] = e
    if error[0]:
        raise error[0]
    return result[0]

def flow_place_order(client: BinanceClient):
    console.print(Panel("[bold yellow]Place a New Order[/bold yellow]", border_style="yellow"))

    symbol = prompt_validated("Symbol", validate_symbol, hint="e.g. BTCUSDT")
    side   = pick_from("Side", SIDES)
    order_type = pick_from("Order Type", ORDER_TYPES)
    qty    = prompt_validated("Quantity", validate_quantity, hint="e.g. 0.05")

    price = stop_price = None
    if order_type in ("LIMIT", "STOP_LIMIT"):
        price = prompt_validated("Limit Price", lambda v: validate_price(v, order_type))
    if order_type == "STOP_LIMIT":
        stop_price = prompt_validated("Stop Price", lambda v: validate_stop_price(v, order_type))

    # Preview table
    console.print()
    preview = Table(title="Order Preview", box=box.SIMPLE_HEAVY, border_style="cyan")
    preview.add_column("Field", style="cyan")
    preview.add_column("Value", style="green bold")
    preview.add_row("Symbol", symbol)
    preview.add_row("Side", side)
    preview.add_row("Type", order_type)
    preview.add_row("Quantity", str(qty))
    if price:    preview.add_row("Limit Price", str(price))
    if stop_price: preview.add_row("Stop Price",  str(stop_price))
    console.print(preview)
    console.print()

    if not Confirm.ask("  [bold]Confirm order?[/bold]", default=True):
        console.print("  [dim]Order cancelled.[/dim]")
        return

    def do_order():
        if order_type == "MARKET":
            return place_market_order(client, symbol, side, qty)
        elif order_type == "STOP_LIMIT":
            return place_stop_limit_order(client, symbol, side, qty, price, stop_price)
        else:
            return place_limit_order(client, symbol, side, qty, price)

    try:
        result = with_spinner("Sending order to Binance...", do_order)
        console.print()
        console.print(Panel(
            f"[bold green]✔ Order Placed Successfully![/bold green]\n\n"
            + format_order_result(result),
            border_style="green",
            title="Result",
        ))
    except APIError as e:
        console.print(Panel(f"[bold red]✘ API Error {e.status_code}:[/bold red] {e.message}", border_style="red"))
    except NetworkError as e:
        console.print(Panel(f"[bold red]✘ Network Error:[/bold red] {e}", border_style="red"))

def flow_check_order(client: BinanceClient):
    console.print(Panel("[bold yellow]Check Order Status[/bold yellow]", border_style="yellow"))
    symbol   = prompt_validated("Symbol", validate_symbol, hint="e.g. BTCUSDT")
    order_id_raw = Prompt.ask("  [bold cyan]Order ID[/bold cyan]")
    try:
        order_id = int(order_id_raw.strip())
    except ValueError:
        console.print("  [bold red]✘[/bold red] Order ID must be an integer.")
        return

    try:
        result = with_spinner("Fetching order from Binance...", lambda: get_order(client, symbol, order_id))
        status  = result.get("status", "?")
        color   = "green" if status == "FILLED" else "yellow" if status == "NEW" else "red"
        console.print()
        console.print(Panel(
            f"[bold {color}]Status: {status}[/bold {color}]\n\n" + format_order_result(result),
            border_style=color,
            title=f"Order #{order_id}",
        ))
    except APIError as e:
        console.print(Panel(f"[bold red]✘ API Error {e.status_code}:[/bold red] {e.message}", border_style="red"))
    except NetworkError as e:
        console.print(Panel(f"[bold red]✘ Network Error:[/bold red] {e}", border_style="red"))

def flow_view_logs(n=20):
    console.print(Panel("[bold yellow]Recent Log Entries[/bold yellow]", border_style="yellow"))
    log_path = "trading_bot.log"
    if not os.path.exists(log_path):
        console.print("  [dim]No log file found. Run some orders first.[/dim]")
        return

    with open(log_path) as f:
        lines = f.readlines()
    tail = lines[-n:] if len(lines) >= n else lines

    table = Table(box=box.SIMPLE, show_header=True, border_style="dim")
    table.add_column("Time", style="dim", no_wrap=True)
    table.add_column("Level", style="bold", no_wrap=True)
    table.add_column("Message", overflow="fold")

    level_colors = {"INFO": "green", "DEBUG": "blue", "WARNING": "yellow", "ERROR": "red"}
    for line in tail:
        parts = line.strip().split(" | ", 3)
        if len(parts) == 4:
            ts, level, _, msg = parts
            color = level_colors.get(level, "white")
            table.add_row(ts, f"[{color}]{level}[/{color}]", msg)
        else:
            table.add_row("", "", line.strip())

    console.print(table)

def main():
    load_dotenv()
    logger = setup_logging()

    api_key    = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    show_banner()

    if not api_key or not api_secret:
        console.print(Panel(
            "[bold red]✘ Missing credentials![/bold red]\n"
            "Create a [bold].env[/bold] file with [cyan]API_KEY[/cyan] and [cyan]API_SECRET[/cyan].",
            border_style="red"
        ))
        return

    client = BinanceClient(api_key, api_secret)
    console.print(f"  [dim]Connected to:[/dim] [bold cyan]{client.base_url}[/bold cyan]")

    while True:
        show_menu()
        choice = Prompt.ask("  [bold white]Select[/bold white]", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            console.print()
            flow_place_order(client)
        elif choice == "2":
            console.print()
            flow_check_order(client)
        elif choice == "3":
            console.print()
            flow_view_logs()
        elif choice == "4":
            console.print("\n  [bold cyan]Goodbye! 👋[/bold cyan]\n")
            break

        console.print()
        Prompt.ask("  [dim]Press Enter to return to menu[/dim]", default="")
        show_banner()

if __name__ == "__main__":
    main()
