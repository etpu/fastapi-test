import subprocess
import time
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Path, Body, Request
from sqlalchemy.orm import Session
from starlette import status

from . import crud, schemas, models
from . import config
from .database import SessionLocal, engine
from .trustedhost import TrustedHostMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Extensions API",
    description="Простой API для управления внутренними номерами IP PBX",
    version="0.7.5",
)
# Включить после тестов V V V
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.vo1p.ru", "127.0.0.1"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Прослойка для учета времени выполнения запросов
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get(
    "/api/extensions",
    response_model=List[schemas.User],
    response_model_exclude_unset=True,
    description="""Получить список всех внутренних номеров: <code>extension</code> с именами сотрудников:
            <code>name</code>, номерами групп/отделов: <code>group_id</code> и их названий <code>title</code>
            <br><br>При использовании флага <code>?short=true</code> можно получить сокращенный спсиок состоящий
        client_host    только из внутреннего номера и имени сотрудника.<br><br> Вместо <code>true / false</code> для удобства
            можно так же использовать значения <code>yes / no</code> <code>on / off</code> <code>1 / 0</code>""",
)
def get_extensions(request: Request, short: bool = False, db: Session = Depends(get_db)):
    client_host = request.client.host
    print(client_host)
    db_extensions = crud.select_extensions_and_group(db, short=short)
    return db_extensions


@app.get(
    "/api/extensions/{extension}",
    response_model=schemas.User,
    response_model_exclude_unset=True,
    description="""Получить данные конкретного внутреннего номера: <code>extension</code> с именем сотрудника:
            <code>name</code>, номером группы/отдела: <code>group_id</code> и названием группы <code>title</code>
            <br><br>При использовании флага <code>?short=true</code> можно получить сокращенный спсиок состоящий
            только из внутреннего номера и имени сотрудника.<br><br> Вместо <code>true / false</code> для удобства
            можно так же использовать значения <code>yes / no</code> <code>on / off</code> <code>1 / 0</code>""",
)
def get_extension(
        extension: str = Path(..., max_length=20, regex=config.REGEX_INT),
        short: bool = False,
        db: Session = Depends(get_db)
):
    db_extension = crud.select_extensions_and_group(db, extension=extension, short=short)
    if db_extension == 404:
        raise HTTPException(status_code=404, detail="User not found")
    return db_extension


@app.get(
    "/api/groups",
    response_model=List[schemas.Group],
    description="""Получить список всех групп(отделов) <code>group_id</code> с их названиями <code>title</code>""",
)
def get_groups(db: Session = Depends(get_db)):
    db_groups = crud.select_groups(db)
    return db_groups


@app.get(
    "/api/groups/{group_id}",
    response_model=List[schemas.User],
    response_model_exclude_unset=True,
    description="""Получить группу(отдел) <code>group_id</code> со всеми входящими в неё внутренними номерами""",
)
def get_group(
        *,
        group_id: str = Path(..., max_length=2, regex=config.REGEX_INT),
        db: Session = Depends(get_db)
):
    db_group = crud.select_extensions_and_group(db, group_id=group_id)
    if db_group == 404:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group


@app.put(
    "/api/extensions/{extension}",
    response_model=schemas.User,
    response_model_exclude_unset=True,
    response_description="Extension changed",
    description="""Изменить у внутреннего номера (<code>extension</code>): Имя сотрудника 
                <code>name</code> и/или номер группы <code>group_id</code>""",
    status_code=status.HTTP_202_ACCEPTED,
)
def change_extension(
        item: schemas.UserIn = Body(
            ...,
            example={
                "name": "Путин ВВ",
                "group_id": "1"
            },
        ),
        extension: str = Path(..., max_length=20, regex=config.REGEX_INT),
        db: Session = Depends(get_db)
):
    db_ext = crud.update_extension(db, extension=extension, item=item)
    if db_ext == 404:
        raise HTTPException(status_code=404, detail="Extension not Found")
    elif db_ext == 422:
        raise HTTPException(status_code=422, detail="Empty Body")
    return db_ext


@app.put(
    "/api/groups/{group_id}",
    response_model=schemas.Group,
    response_description="Group changed",
    description="Изменить группу(отдел) с уникальным id группы <code>group_id</code> и названием <code>title</code>",
    status_code=status.HTTP_202_ACCEPTED,
)
def change_group(
        group: schemas.GroupIn,
        group_id: str = Path(..., max_length=2, regex=config.REGEX_INT),
        db: Session = Depends(get_db)
):
    db_group = crud.update_group(db, group_id=group_id, title=group.title)
    if db_group == 404:
        raise HTTPException(status_code=404, detail="Group not Found")
    return db_group


@app.post(
    "/api/groups/{group_id}",
    response_model=schemas.Group,
    response_description="Group created",
    description="Создать группу/отдел с уникальным id группы <code>group_id</code> и названием <code>title</code>",
    status_code=status.HTTP_201_CREATED,
)
def create_group(
        group: schemas.GroupIn,
        group_id: str = Path(..., max_length=2, regex=config.REGEX_INT),
        db: Session = Depends(get_db)
):
    db_group = crud.insert_group(db, group_id=group_id, title=group.title)
    if db_group == 400:
        raise HTTPException(status_code=400, detail="Group already exist")
    return db_group


@app.delete(
    "/api/groups/{group_id}",
    response_description="Group deleted",
    description="Удалить существующую группу/отдел с уникальным id <code>group_id</code>",
    status_code=status.HTTP_202_ACCEPTED,
)
def delete_group(group_id: str = Path(..., max_length=2, regex=config.REGEX_INT), db: Session = Depends(get_db)):
    db_delete = crud.delete_group(db, group_id)
    if db_delete == 404:
        raise HTTPException(status_code=404, detail="Group not Found")


@app.post("/apply")
def apply_config():
    apply_status = subprocess.call(["amportal", "a", "r"])
    if apply_status != 0:
        raise HTTPException(status_code=400, detail="Somthing wrong!")
