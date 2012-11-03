def count_delivery_price(price, weight):
    if price < 10:
        return 5.0
    elif price < 20:
        return 2.0
    else:
        return 0.0
