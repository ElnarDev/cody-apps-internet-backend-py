from typing import Any
from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.category import CategoryPublic, CategoryCreate, CategoryUpdate
from app.services import category_service

router = APIRouter()


@router.post("/", response_model=CategoryPublic)
def create_category(
    *, session: SessionDep, current_user: CurrentUser, category_in: CategoryCreate
) -> Any:
    return category_service.create_category(session=session, category_in=category_in)


@router.get("/", response_model=list[CategoryPublic])
def read_categories(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    return category_service.get_categories(session=session, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryPublic)
def read_category(
    category_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    category = category_service.get_category_by_id(
        session=session, category_id=category_id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryPublic)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    category = category_service.get_category_by_id(
        session=session, category_id=category_id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category_service.update_category(
        session=session, db_item=category, category_in=category_in
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int, session: SessionDep, current_user: CurrentUser
) -> Any:
    category = category_service.get_category_by_id(
        session=session, category_id=category_id
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_service.delete_category(session=session, db_item=category)
    return {"message": "Category deleted successfully"}
