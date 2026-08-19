import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ShortLink
from app.schemas.short_link import ShortLinkCreate, ShortLinkUpdate, ShortLinkOut
from app.auth.dependencies import get_current_user
from app.services.code_generator import generate_short_code
from app.config import settings

router = APIRouter(prefix="/links", tags=["links"])


def build_link_out(link: ShortLink) -> ShortLinkOut:
    return ShortLinkOut(
        id=link.id,
        short_code=link.short_code,
        original_url=link.original_url,
        short_url=f"{settings.base_url}/{link.short_code}",
        is_active=link.is_active,
        expires_at=link.expires_at,
        max_clicks=link.max_clicks,
        created_at=link.created_at,
        click_count=len(link.clicks),
    )


def get_link_or_404(link_id: uuid.UUID, db: Session, current_user: User) -> ShortLink:
    link = (
        db.query(ShortLink)
        .filter(ShortLink.id == link_id, ShortLink.owner_id == current_user.id)
        .first()
    )
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return link


@router.post("", response_model=ShortLinkOut, status_code=status.HTTP_201_CREATED)
def create_link(
    link_in: ShortLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if link_in.custom_alias:
        existing = db.query(ShortLink).filter(ShortLink.short_code == link_in.custom_alias).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This alias is already taken",
            )
        short_code = link_in.custom_alias
    else:
        short_code = generate_short_code()
        while db.query(ShortLink).filter(ShortLink.short_code == short_code).first():
            short_code = generate_short_code()

    link = ShortLink(
        short_code=short_code,
        original_url=str(link_in.original_url),
        expires_at=link_in.expires_at,
        max_clicks=link_in.max_clicks,
        owner_id=current_user.id,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return build_link_out(link)


@router.get("", response_model=list[ShortLinkOut])
def list_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = (
        db.query(ShortLink)
        .filter(ShortLink.owner_id == current_user.id)
        .order_by(ShortLink.created_at.desc())
        .all()
    )
    return [build_link_out(link) for link in links]


@router.get("/{link_id}", response_model=ShortLinkOut)
def get_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = get_link_or_404(link_id, db, current_user)
    return build_link_out(link)


@router.patch("/{link_id}", response_model=ShortLinkOut)
def update_link(
    link_id: uuid.UUID,
    link_in: ShortLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = get_link_or_404(link_id, db, current_user)
    for field, value in link_in.model_dump(exclude_unset=True).items():
        setattr(link, field, value)
    db.commit()
    db.refresh(link)
    return build_link_out(link)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = get_link_or_404(link_id, db, current_user)
    db.delete(link)
    db.commit()