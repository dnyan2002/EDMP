from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def float_or_question(value, precision=1):
    if value == "?":
        return "?"
    try:
        return f"{float(value):.{precision}f}"
    except:
        return "?"
