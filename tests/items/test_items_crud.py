from backend.items import crud


def test_get_item(session, item):
    t_item = crud.get_item(session, item.id)
    assert t_item.id == item.id
