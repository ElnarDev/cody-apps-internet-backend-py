from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models.product import ProductCreate, ProductPublic, ProductUpdate
from app.services import product_service

router = APIRouter()

@router.get("/", response_model=list[ProductPublic])
def read_products(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    return product_service.get_products(session=session, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductPublic)
def read_product(session: SessionDep, current_user: CurrentUser, product_id: int) -> Any:
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado ❌")
    return product

@router.post("/", response_model=ProductPublic)
def create_product(session: SessionDep, current_user: CurrentUser, product_in: ProductCreate) -> Any:
    return product_service.create_product(session=session, product_in=product_in)

@router.patch("/{product_id}", response_model=ProductPublic)
def update_product(session: SessionDep, current_user: CurrentUser, product_id: int, product_in: ProductUpdate) -> Any:
    product_db = product_service.update_product(session=session, product_id=product_id, product_in=product_in)
    if not product_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado ❌")
    return product_db

@router.delete("/{product_id}")
def delete_product(session: SessionDep, current_user: CurrentUser, product_id: int) -> dict:
    deleted = product_service.delete_product(session=session, product_id=product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado ❌")
    return {"mensaje": f"Producto {product_id} borrado exitosamente de la base de datos"}
