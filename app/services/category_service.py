from sqlmodel import Session, select
from app.models.category import Category, CategoryCreate, CategoryUpdate


def create_category(*, session: Session, category_in: CategoryCreate) -> Category:
    db_item = Category.model_validate(category_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_categories(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Category]:
    statement = select(Category).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_category_by_id(*, session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)


def update_category(
    *, session: Session, db_item: Category, category_in: CategoryUpdate
) -> Category:
    update_data = category_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_category(*, session: Session, db_item: Category) -> None:
    session.delete(db_item)
    session.commit()
