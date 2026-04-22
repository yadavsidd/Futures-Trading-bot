import os
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from bot.logging_config import setup_logging
from bot.client import BinanceClient, APIError, NetworkError
from bot.orders import place_market_order, place_limit_order, place_stop_limit_order, get_order, format_order_result
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price
)

app = typer.Typer(help="Binance Futures CLI Trading Bot")
console = Console()

@app.command()
def place_order(
    symbol: str = typer.Option(..., "--symbol", help="Trading symbol, e.g., BTCUSDT"),
    side: str = typer.Option(..., "--side", help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--type", help="Order type: MARKET, LIMIT, or STOP_LIMIT"),
    quantity: str = typer.Option(..., "--quantity", help="Order quantity in asset units"),
    price: str = typer.Option(None, "--price", help="Target price (required only for LIMIT/STOP_LIMIT orders)"),
    stop_price: str = typer.Option(None, "--stop-price", help="Stop price (required only for STOP_LIMIT orders)")
):
    """
    Validates and places an order on Binance Futures Testnet.
    """
    # 1. Setup logging
    logger = setup_logging()
    
    # 2. Load API credentials
    load_dotenv()
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    
    if not api_key or not api_secret:
        console.print("[bold red]Error:[/bold red] API_KEY and API_SECRET must be defined in the .env file")
        raise typer.Exit(code=1)

    # 3. Validation
    try:
        val_symbol = validate_symbol(symbol)
        val_side = validate_side(side)
        val_type = validate_order_type(order_type)
        val_qty = validate_quantity(quantity)
        val_price = validate_price(price, val_type)
        val_stop_price = validate_stop_price(stop_price, val_type)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 4. Print summary table
    table = Table(title="Order Confirmation Draft")
    table.add_column("Property", justify="left", style="cyan", no_wrap=True)
    table.add_column("Value", justify="left", style="green")

    table.add_row("Symbol", val_symbol)
    table.add_row("Side", val_side)
    table.add_row("Type", val_type)
    table.add_row("Quantity", str(val_qty))
    if val_price is not None:
        table.add_row("Price", str(val_price))
    if val_stop_price is not None:
        table.add_row("Stop Price", str(val_stop_price))

    console.print()
    console.print(table)
    console.print()

    # 5. Place order
    client = BinanceClient(api_key, api_secret)
    console.print("[yellow]Dispatching order to Binance...[/yellow]")
    
    try:
        if val_type == "MARKET":
            result = place_market_order(client, val_symbol, val_side, val_qty)
        elif val_type in ("STOP_LIMIT", "STOP"):
            result = place_stop_limit_order(client, val_symbol, val_side, val_qty, val_price, val_stop_price)
        else:
            result = place_limit_order(client, val_symbol, val_side, val_qty, val_price)
            
        # 6. Success Output
        console.print("[bold green]Order execution successful![/bold green]\n")
        console.print(format_order_result(result))
        
    # 7. Error Handling
    except APIError as e:
        console.print(f"[bold red]Binance API Error:[/bold red] {e.message} (HTTP {e.status_code})")
        raise typer.Exit(code=1)
    except NetworkError as e:
        console.print(f"[bold red]Network Connection Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Unexpected Application Error:[/bold red] {e}")
        logger.exception("Unexpected error occurred while placing order.")
        raise typer.Exit(code=1)

@app.command("get-order")
def check_order(
    symbol: str = typer.Option(..., "--symbol", help="Trading symbol, e.g., BTCUSDT"),
    order_id: int = typer.Option(..., "--order-id", help="Order ID returned when the order was placed")
):
    """Fetch and display the current status of an existing order."""
    logger = setup_logging()
    load_dotenv()
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    if not api_key or not api_secret:
        console.print("[bold red]Error:[/bold red] API_KEY and API_SECRET must be defined in the .env file")
        raise typer.Exit(code=1)

    try:
        sym = validate_symbol(symbol)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    client = BinanceClient(api_key, api_secret)
    try:
        result = get_order(client, sym, order_id)
        console.print(f"[bold green]Order found![/bold green]\n")
        console.print(format_order_result(result))
    except APIError as e:
        console.print(f"[bold red]Binance API Error:[/bold red] {e.message} (HTTP {e.status_code})")
        raise typer.Exit(code=1)
    except NetworkError as e:
        console.print(f"[bold red]Network Connection Error:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
