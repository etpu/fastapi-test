from sqlalchemy.orm import Session

from . import models, schemas


def select_extensions_and_group(db: Session, extension: str = None, group_id: str = None, short: bool = False):
    if short:
        query = db.query(models.User.extension, models.User.name)
    else:
        query = db.query(
            models.Sip.id.label("extension"),
            models.User.name,
            models.Sip.data.label("group_id"),
            models.Group.title,
        ) \
            .join(models.User, models.Sip.id == models.User.extension) \
            .outerjoin(models.Group, models.Sip.data == models.Group.group_id) \
            .filter(models.Sip.keyword == "callgroup")
    if extension:
        query = query.filter(models.User.extension == extension).order_by(models.User.extension).first()
        if not query:
            return 404
        return query
    if group_id:
        query = query.filter(models.Sip.data == group_id).all()
        if not query:
            return 404
        return query
    return query.order_by(models.User.extension).all()


def select_groups(db: Session):
    return db.query(models.Group).all()


def update_group(db: Session, group_id, title: str):
    query = db.query(models.Group).filter_by(group_id=group_id).update({'title': title})
    if not query:
        return 404
    db.commit()
    return {"group_id": group_id, "title": title}


def update_extension(db: Session, extension: str, item: schemas.UserIn):  # Изменяем group и/или name
    out = {"extension": extension}
    query = db.query(models.User).filter_by(extension=extension)
    if not query.first():
        return 404
    if item.name:
        query.update({'name': item.name})
        db.query(models.Device).filter_by(id=extension).update({'description': item.name})
        db.commit()
        out.update({"name": item.name})
    if item.group_id:
        db.query(models.Sip).filter_by(id=extension).filter_by(keyword="callgroup").update({'data': item.group_id})
        db.query(models.Sip).filter_by(id=extension).filter_by(keyword="pickupgroup").update({'data': item.group_id})
        db.commit()
        out.update({"group_id": item.group_id})
    return out


def insert_group(db: Session, group_id, title: str):
    query = db.query(models.Group).filter_by(group_id=group_id).first()
    if query:
        return 400
    db_group = models.Group(group_id=group_id, title=title)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def delete_group(db: Session, group_id: str):
    query = db.query(models.Group).filter_by(group_id=group_id).delete()
    if query:
        db.commit()
        return
    return 404
