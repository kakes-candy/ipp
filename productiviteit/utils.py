

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


def lijst_jaren():
    import datetime
    # lijst met jaren maken, huidig jaar en 2 jaar ervoor, maar niet lager dan 2016
    # het zou mooier zijn om te kijken welke jaren in de data zitten, maar dat kost teveel tijd
    jaren = []
    # 1 januari van dit jaar opslaan
    vandaag = datetime.datetime.today().date().replace(month=1).replace(day=1)
    for i in range(0, 3):
        date = vandaag.replace(year=(vandaag.year-i))
        if date.year >= 2016:
            jaren.append(date)
    return(jaren)
