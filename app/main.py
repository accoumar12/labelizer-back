from fastapi import FastAPI

app = FastAPI()

@app.get('/api/labelizer/pairs')
def make_labelizer_pairs(user_id: str) -> LabelizerPairsResponse:
    # todo generate pairs
    return LabelizerPairsResponse(
        request_id='request_id',
        reference_id='reference_id',
        left_id='left_id',
        right_id='right_id',
    )


@app.post('/api/labelizer/pairs')
def set_labelizer_pairs(user_id: str, request_id: str = Form(), label: SelectedItemType = Form()) -> None:
    
    # todo store selected ref with selected id
    

@app.get("/api/labelizer/images/{image_id}")
def get_image(user_id: str, image_id: str):
    return FileResponse(f"images/{image_id}.png")
