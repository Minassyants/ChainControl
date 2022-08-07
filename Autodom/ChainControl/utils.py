colors = {
    'OP':'text-primary',
    'OA':'text-primary',
    'AP':'text-success',
    'OR':'text-warning',
    'CA':'text-danger',
    'DO':'text-success',
    }


def set_approval_color(els):
    for el in els:
        el.color = colors[el.new_status]
