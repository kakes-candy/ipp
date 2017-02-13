

def get_role(employee):
    from productiviteit.models import Employee

    # verschillende aspecten van de rol
    # worden vastgelegd in dict
    rol = {}
    # Gebruikers object ook opslaan
    rol['gebruiker'] = employee

    # Vestiging erbij
    rol['vestiging'] = employee.vestiging.pk

    # Eventuele teamleden ophalen
    rol['tl'] = Employee.objects.filter(vestiging__teamleider = employee)

    # Als er teamleden zijn, dan is employee teamleider
    if rol['tl'].exists():
        rol['naam'] = 'teamleider'
    # anders maar een gewone behandelaar
    else:
        rol['naam'] = 'behandelaar'

    return rol

def has_permission(test_id, rol, niveau):
    if niveau == 'individueel':
        return (test_id == rol['gebruiker'].pk or rol['tl'].filter(pk = test_id).exists())
    if niveau == 'vestiging':
        return (test_id == rol['vestiging'] and rol['naam'] == 'teamleider')
