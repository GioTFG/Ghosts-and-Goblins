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

def remove_pos(pos1: Point, pos2: Point) -> Point:
    """
    Sottrae componente per componente da pos1 pos2.\n
    Es: (10, 9) - (4, 1) = (6, 8)
    """
    return pos1[0] - pos2[0], pos1[1] - pos2[1]