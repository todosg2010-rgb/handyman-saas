from typing import Dict, List

SETTINGS = {
    "transport_per_km": 1.20,
    "visit_fee": 15.0,
    "min_offer": 120.0
}

def изчисли_оферта(data: Dict) -> Dict:
    description = data.get("description", "")
    hours = float(data.get("hours", 0))
    hourly_rate = float(data.get("hourly_rate", 0))
    profit_percent = float(data.get("profit_percent", 0))
    distance = float(data.get("distance", 0))

    input_materials = data.get("materials", [])

    # -----------------------
    # MATERIALS COST
    # -----------------------
    materials_cost = 0.0
    materials: List[Dict] = []

    for m in input_materials:
        price = float(m.get("unit_price", 0))
        qty = float(m.get("quantity", 0))
        total = round(price * qty, 2)

        materials_cost += total
        materials.append({
            "name": m.get("name"),
            "unit_price": price,
            "quantity": qty,
            "total_price": total
        })

    # -----------------------
    # TRANSPORT COST
    # -----------------------
    transport = round(
        SETTINGS["visit_fee"] + distance * SETTINGS["transport_per_km"], 2
    )

    # -----------------------
    # LABOR INCOME (NOT COST)
    # -----------------------
    labor_income = round(hours * hourly_rate, 2)

    # -----------------------
    # BASE COST (REAL EXPENSES)
    # -----------------------
    base_cost = round(materials_cost + transport, 2)

    # -----------------------
    # EXTRA PROFIT
    # -----------------------
    extra_profit = round(
        (base_cost + labor_income) * (profit_percent / 100), 2
    )

    # -----------------------
    # FINAL PRICE
    # -----------------------
    final_price = round(
        base_cost + labor_income + extra_profit, 2
    )

    if final_price < SETTINGS["min_offer"]:
        final_price = SETTINGS["min_offer"]

    # -----------------------
    # REAL PROFIT
    # -----------------------
    real_profit = round(labor_income + extra_profit, 2)

    margin = round((real_profit / final_price) * 100, 2) if final_price else 0

    # -----------------------
    # CLIENT MESSAGE
    # -----------------------
    client_message = (
        f"Здравейте,\n\n"
        f"Относно \"{description}\":\n\n"
        f"Материали: {materials_cost:.2f} €\n"
        f"Труд ({hours} ч. × {hourly_rate} €): {labor_income:.2f} €\n"
        f"Транспорт: {transport:.2f} €\n\n"
        f"Крайна цена: {final_price:.2f} €\n\n"
        f"Поздрави,"
    )

    return {
        "description": description,
        "hours": hours,
        "hourly_rate": hourly_rate,
        "profit_percent": profit_percent,
        "distance": distance,

        "materials": materials,

        "costs": {
            "materials": materials_cost,
            "transport": transport,
            "base_cost": base_cost
        },

        "income": {
            "labor": labor_income,
            "extra_profit": extra_profit,
            "total_profit": real_profit,
            "margin_percent": margin
        },

        "final_price": final_price,
        "client_message": client_message,
        "engine_version": "v3.0"
    }
