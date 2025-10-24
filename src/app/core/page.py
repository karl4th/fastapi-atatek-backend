from sqlalchemy.ext.asyncio import AsyncSession
from src.app.schemas.page import (
    PageBase, 
    CreatePage, 
    UpdatePage,
    ModeratorBase,
    FullPageResponse,
    PageListResponse
)
from src.app.models import Page, User, PageModerator
from src.app.utils.cache import UserCache
from sqlalchemy.future import select
from fastapi import HTTPException, status

class PageService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_cache = UserCache()

    async def get_pages(
        self, skip: int = 0, limit: int = 10
    ) -> PageListResponse:
        try:
            stmp = await self.db.execute(
                select(Page).offset(skip).limit(limit)
            )
            result = stmp.scalars().all()
            return PageListResponse(
                items=[PageBase.model_validate(item.__dict__) for item in result],
                total=len(result),
                limit=limit,
                offset=skip
            )
        except Exception as e:
            raise e

    async def get_page_by_id(
        self, page_id: int
    ):
        try:
            stmp = await self.db.execute(
                select(Page).where(Page.id == page_id)
            )
            page = stmp.scalars().first()
            if not page:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Парақша табылмады"
                )
            # Get moderators
            stmp_mod = await self.db.execute(
                select(User).join(PageModerator).where(PageModerator.page_id == page_id)
            )
            moderators = stmp_mod.scalars().all()
            return FullPageResponse(
                **PageBase.model_validate(page.__dict__).model_dump(),
                moderators=[ModeratorBase.model_validate(mod.__dict__) for mod in moderators]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Парақшаны алу кезінде қате пайда болды"
            )

    async def search_pages(
        self,
        main_gen: int,
        main_gen_child: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> PageListResponse:
        try:

            if main_gen_child is not None:
                stmp = await self.db.execute(
                    select(Page).where(
                        Page.main_gen == main_gen,
                        Page.main_gen_child == main_gen_child
                    ).offset(skip).limit(limit)
                )
            if main_gen_child is None:
                stmp = await self.db.execute(
                    select(Page).where(
                        Page.main_gen == main_gen,
                    ).offset(skip).limit(limit)
                )
            result = stmp.scalars().all()

            return PageListResponse(
                items=[PageBase.model_validate(item.__dict__) for item in result],
                total=len(result),
                limit=limit,
                offset=skip
            )
        except Exception as e:
            raise e

    async def create_page(
        self, 
        payload: CreatePage
    ):
        try:
            new_page = Page(
                title=payload.title,
                tree_id=payload.tree_id,
                bread1=payload.bread1,
                bread2=payload.bread2,
                bread3=payload.bread3,
                main_gen=payload.main_gen_id,
                main_gen_child=payload.main_gen_child_id,
            )
            self.db.add(new_page)
            await self.db.commit()
            await self.db.refresh(new_page)
            return PageBase.model_validate(new_page.__dict__)
        except Exception as e:
            raise e

    async def update_page(
        self, 
        user_id: int,
        page_id: int, 
        payload: UpdatePage
    ):
        try: 
            stmp = await self.db.execute(
                select(Page).where(Page.id == page_id)
            )
            page = stmp.scalars().first()
            if not page:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Парақша табылмады"
                )
            
            update_data = payload.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(page, key, value)

            await self.db.commit()
            await self.db.refresh(page)
            await self.user_cache.invalidate(user_id)
            return PageBase.model_validate(page.__dict__)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Парақшаны жаңарту кезінде қате пайда болды: {str(e)}"
            )

    async def delete_page(
        self, 
        page_id: int
    ):
        try:
            stmp = await self.db.execute(
                select(Page).where(Page.id == page_id)
            )
            page = stmp.scalars().first()
            if not page:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Парақша табылмады"
                )
            await self.db.delete(page)
            await self.db.commit()
            return {"detail": "Парақша сәтті жойылды"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Парақшаны жою кезінде қате пайда болды"
            )

    async def add_moderator(
        self, 
        user_id: int,
        page_id: int
    ):
        try: 
            new_moderator = PageModerator(
                page_id=page_id,
                user_id=user_id
            )
            self.db.add(new_moderator)
            await self.db.commit()
            await self.db.refresh(new_moderator)
            return {"detail": "Модератор сәтті қосылды"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Модераторды қосу кезінде қате пайда болды"
            )   
    
    async def remove_moderator(
        self,
        moderator_id: int
    ):
        try: 
            stmp = await self.db.execute(
                select(PageModerator).where(PageModerator.id == moderator_id)
            )
            moderator = stmp.scalars().first()
            if not moderator:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Модератор табылмады"
                )
            await self.db.delete(moderator)
            await self.db.commit()
            return {"detail": "Модератор сәтті жойылды"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Модераторды жою кезінде қате пайда болды"
            )

    async def set_page_user(
        self,
        user_id: int,
        page_id: int
    ):
        stmp = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = stmp.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Қолданушы табылмады"
            )
        user.page_id = page_id
        await self.db.commit()
        await self.db.refresh(user)
        await self.user_cache.invalidate(user_id)
        return {"detail": "Пайдаланушының парақшасы сәтті орнатылды"}