from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from src.auth.auth import get_current_user
from src.database.database import get_db
from src.publications.models import Publication, DeletedPublication
from src.schemas import PublicationOut, PublicationCreate, PublicationUpdate, DeletedPublicationOut
from src.auth.models import User


publ_router = APIRouter()

from src.schemas import PaginatedResponse
from sqlalchemy import func


@publ_router.get("/get_all", response_model=PaginatedResponse[PublicationOut])
async def get_all_publications(
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(10, ge=1, le=100, description="Количество на странице"),
        db: AsyncSession = Depends(get_db)
):
    # Общее количество записей
    total = await db.scalar(select(func.count()).select_from(Publication))

    # Пагинация
    offset = (page - 1) * page_size
    query = select(Publication).offset(offset).limit(page_size).order_by(Publication.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@publ_router.post("/create", response_model=PublicationOut)
async def create_publication(
        pub_data: PublicationCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
        ):

    new_publication = Publication(**pub_data.model_dump(),
                                  author_id=current_user.id
                                  )
    db.add(new_publication)

    await db.commit()
    await db.refresh(new_publication)
    return new_publication


@publ_router.patch("/edit/{publication_id}", response_model=PublicationOut)
async def edit_publication(
    publication_id: UUID,
    update_data: PublicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Находим публикацию
    result = await db.execute(select(Publication).where(Publication.publication_id == publication_id))
    publication = result.scalar_one_or_none()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    #Проверяем, что пользователь -- автор
    if publication.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Обновляем только те поля, которые были переданы
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(publication, key, value)

    # Обновляем updated_at вручную (если не хотим полагаться на onupdate)
    # SQLAlchemy с onupdate=func.now() должен сам обновить, но явно не помешает
    # publication.updated_at = func.now() - лучше оставить автоматическое обновление в модели

    await db.commit()
    await db.refresh(publication)
    return publication



@publ_router.delete("/delete/{publication_id}", status_code=204)
async def soft_delete_publication(
        publication_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Находим публикацию
    result = await db.execute(select(Publication).where(Publication.publication_id == publication_id))
    publication = result.scalar_one_or_none()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")

    if publication.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Копируем в удалённые
    deleted = DeletedPublication(
        publication_id=publication.publication_id,
        title=publication.title,
        text=publication.text,
        category=publication.category,
        image_url=publication.image_url,
        created_at=publication.created_at,
        updated_at=publication.updated_at,
        author_id=publication.author_id
        # deleted_at заполнится автоматически
    )
    db.add(deleted)
    await db.delete(publication)
    await db.commit()


#Получаем удалённые статьи
@publ_router.get("/deleted", response_model=PaginatedResponse[DeletedPublicationOut])
async def get_deleted_publications(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    total = await db.scalar(select(func.count()).select_from(DeletedPublication))
    offset = (page - 1) * page_size
    result = await db.execute(select(DeletedPublication).offset(offset).limit(page_size).order_by(DeletedPublication.deleted_at.desc()))
    items = result.scalars().all()
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)

#восстанавливаем удалённую публикацию
@publ_router.post("/restore/{publication_id}", response_model=PublicationOut)
async def restore_publication(
        publication_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Находим удалённую публикацию
    result = await db.execute(select(DeletedPublication).where(DeletedPublication.publication_id == publication_id))
    deleted = result.scalar_one_or_none()
    if not deleted:
        raise HTTPException(status_code=404, detail="Deleted publication not found")

    # Проверяем права (опционально: только автор может восстановить)
    if deleted.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Восстанавливаем
    restored = Publication(
        publication_id=deleted.publication_id,
        title=deleted.title,
        text=deleted.text,
        category=deleted.category,
        image_url=deleted.image_url,
        created_at=deleted.created_at,
        updated_at=deleted.updated_at,
        author_id=deleted.author_id
    )
    db.add(restored)
    await db.delete(deleted)
    await db.commit()
    await db.refresh(restored)
    return restored