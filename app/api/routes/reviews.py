from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.models.review import ReviewCreate, ReviewPublic
from app.services import review_service

router = APIRouter()

@router.get("/{product_id}", response_model=list[ReviewPublic])
def read_reviews(
    session: SessionDep,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    # Las reseñas son públicas (cualquiera puede leerlas sin estar logueado)
    return review_service.get_reviews_by_product(
        session=session, product_id=product_id, skip=skip, limit=limit
    )


@router.post("/{product_id}/reviews", response_model=ReviewPublic)
def create_review(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    product_id: int,
    review_in: ReviewCreate,
) -> Any:
    # VULNERABILIDAD CRÍTICA EVITADA: Extraemos el ID del usuario autenticado directamente de `current_user.id`
    # y el ID del producto de la URL (path parameter). El frontend no puede suplantar la identidad de otro usuario.
    
    # Nos aseguramos de que current_user.id no sea None
    assert current_user.id is not None
    
    return review_service.create_review(
        session=session,
        review_in=review_in,
        user_id=current_user.id,
        product_id=product_id,
    )

