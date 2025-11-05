from .actor import Point

def center(pos: Point, size: Point) -> Point:
    """
    Calcola il pixel "centrale" data posizione (in alto a sinistra) e dimensione (per avere l'angolo in basso a destra.
    :param pos: La posizione, cioè il pixel più in alto a destra dell'oggetto.
    :param size: La dimensione, cioè la quantità di pixel di larghezza e di altezza dell'oggetto
    :return: La posizione (assoluta) del pixel centrale.
    """
    x, y, w, h = pos + size
    return x + w / 2, y + h / 2