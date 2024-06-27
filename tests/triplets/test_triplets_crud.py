def test_get_triplet(session, triplet):
    from backend.triplets import crud

    t_triplet = crud.get_first_unlabeled_triplet(session)
    assert t_triplet.id == triplet.id


def test_get_validation_triplet(session, validation_triplet):
    from backend.triplets import crud

    t_validation_triplet = crud.get_first_unlabeled_validation_triplet(session)
    assert t_validation_triplet.id == validation_triplet.id
