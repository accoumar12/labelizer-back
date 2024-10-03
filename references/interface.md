Details of the interface used.

1. Login
2. Call GET /api/labelizer/pairs
3. Call GET /api/labelizer/images/{image_id} on each id (left, right, ref)
4. Call POST /api/labelizer/pairs with label

app = FastAPI()

@dataclass
class LabelizerPairsResponse:
    request_id: str
    ref_id: str
    left_id: str
    right_id: str

@app.get('/api/labelizer/pairs')
def make_labelizer_pairs(user_id: str) -> LabelizerPairsResponse:

    # todo generate pairs
    
    return LabelizerPairsResponse(
        request_id='request_id',
        ref_id='ref_id',
        left_id='left_id',
        right_id='right_id',
    )

@app.post('/api/labelizer/pairs')
def set_labelizer_pairs(user_id: str, request_id: str = Form(), label: SelectedItemType = Form()) -> None:

    # todo store selected ref with selected id

@app.get("/api/labelizer/images/{image_id}")
def get_image(user_id: str, image_id: str):
    return FileResponse(f"images/{image_id}.png")

---------------------

table name: triplet_labeled

class SelectedItemType(StrEnum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'

@dataclass
class TripletLabeled:
    id: str
    ref_id: str
    left_id: str
    right_id: str
    label: SelectedItemType | None  = None
    user_id: str | None = None

select * from triplet_labeled where label is not null limit 1
