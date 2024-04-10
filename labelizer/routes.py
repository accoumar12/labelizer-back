from fastapi import APIRouter, status

from labelizer.model import LabelizerTripletResponse

router = APIRouter(tags=["Studies Management"])


@router.get(
    "/triplet",
    summary="TODO",
    status_code=status.HTTP_200_OK,
)
async def make_labelizer_triplet(
) -> LabelizerTripletResponse:
    """
    TODO
    """
    # todo get from db with a logic...
    # with get_db() as session:
    #     result = get_triplet(session)

    result = LabelizerTripletResponse("0", "0", "0", "0")

    return result
