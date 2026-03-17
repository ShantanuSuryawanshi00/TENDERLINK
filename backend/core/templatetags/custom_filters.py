from django import template

register = template.Library()

@register.filter
def eq(value, arg):
    """
    Returns True if value == arg, else False.
    Usage: {% if value|eq:arg %}
    """
    return value == arg

@register.filter
def currency_in(value):
    """
    Formats a number with Indian currency commas.
    Example: 10000000 -> 1,00,00,000.00
    """
    try:
        if value is None:
            return "₹0.00"
        value = float(value)
    except (TypeError, ValueError):
        return value
    
    s = f"{value:.2f}"
    parts = s.split('.')
    main = parts[0]
    decimal = parts[1]
    
    # Handle negative numbers
    is_negative = main.startswith('-')
    if is_negative:
        main = main[1:]
    
    if len(main) > 3:
        last_three = main[-3:]
        rest = main[:-3]
        groups = []
        while rest:
            groups.append(rest[-2:])
            rest = rest[:-2]
        main = ",".join(reversed(groups)) + "," + last_three
    
    res = f"₹{main}.{decimal}"
    if is_negative:
        res = f"-{res}"
    return res
