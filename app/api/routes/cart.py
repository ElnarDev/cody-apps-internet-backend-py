from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.models.cart_item import CartItemCreate, CartItemPublic
from app.services import cart_service

router = APIRouter()


@router.get("/", response_model=list[CartItemPublic])
def get_my_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    # Extraemos el user_id del token JWT para mostrar SOLO el carrito del usuario autenticado
    assert current_user.id is not None
    return cart_service.get_cart(session=session, user_id=current_user.id)


@router.post("/", response_model=CartItemPublic)
def add_item_to_cart(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    cart_in: CartItemCreate,
) -> Any:
    # VULNERABILIDAD CRÍTICA EVITADA: Extraemos el ID del usuario directamente de `current_user.id`
    # y no del JSON enviado en el cuerpo de la petición.
    assert current_user.id is not None

    return cart_service.add_to_cart(
        session=session,
        cart_in=cart_in,
        user_id=current_user.id,
    )
