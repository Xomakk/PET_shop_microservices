from fastapi.routing import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(path="/login")
def login():
    pass


@router.post(path="/register")
def register():
    pass


@router.post(path="/logout")
def logout():
    pass
