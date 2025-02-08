from fastapi import APIRouter, Request, HTTPException, Response, Depends
from sqlalchemy import select
from starlette import status
from database.connect import SessionDep
from database.models.base import UserModel, TokenModel
from dto.requests.api_auth import LoginRequestApiAuthDTO, RegistrationRequestApiAuthDTO
from dto.resources.api_auth import AuthResourcesDTO, RegistrationResourcesDTO
from service.api_auth import hash_password, verify_password, create_jwt_token, jwt_checker, TokenType

api_auth_router = APIRouter(prefix="/api/auth", tags=["api_auth"])


@api_auth_router.post('/login', response_model=AuthResourcesDTO, status_code=status.HTTP_200_OK)
async def post_authorization(data: LoginRequestApiAuthDTO, session: SessionDep, response: Response):
    query = await session.execute(
        select(UserModel).filter((UserModel.username == data.username))
    )

    existing_user = query.scalar_one_or_none()

    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username not have")
    elif verify_password(data.password, existing_user.password) is False:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Password not current")

    token_query = await session.execute(
        select(TokenModel).filter(TokenModel.user_id == existing_user.id)
    )
    active_tokens = token_query.scalars().all()

    if len(active_tokens) >= 10:
        for user_data_token in active_tokens[:len(active_tokens) - 9]:
            await session.delete(user_data_token)

    token_data = {
        "user_id": existing_user.id,
        "username": existing_user.username,
        "email": existing_user.email
    }

    jwt_token = create_jwt_token(token_data, int(TokenType.access.value))
    new_token = TokenModel(user_id=existing_user.id, access_token=jwt_token)

    response.set_cookie(key="access_token", value=jwt_token)
    session.add(new_token)
    await session.flush()
    await session.commit()
    await session.refresh(new_token)
    return AuthResourcesDTO(access_token=new_token.access_token, user_id=new_token.user_id, username=existing_user.username,
                            email=existing_user.email)


@api_auth_router.post('/registration', response_model=RegistrationResourcesDTO, status_code=status.HTTP_201_CREATED)
async def post_registration(data: RegistrationRequestApiAuthDTO, session: SessionDep):
    existing_user = await session.execute(
        select(UserModel).filter((UserModel.username == data.username) | (UserModel.email == data.email))
    )
    if existing_user.scalar() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered")

    new_user = UserModel(
        username=data.username,
        password=hash_password(data.password),
        email=data.email,
        birthday=data.birthday,
    )

    session.add(new_user)
    await session.flush()
    await session.commit()
    await session.refresh(new_user)
    return RegistrationResourcesDTO(user_id=new_user.id, username=new_user.username, email=new_user.email)


@api_auth_router.get('/me', response_model=AuthResourcesDTO, status_code=status.HTTP_200_OK)
async def get_me_info(request: Request, payload: str = Depends(jwt_checker)):
    return AuthResourcesDTO(
        access_token=request.cookies.get("access_token"),
        user_id=int(payload["user_id"]),
        username=payload["username"],
        email=payload["email"]
    )


@api_auth_router.patch('/switch_password', status_code=status.HTTP_205_RESET_CONTENT)
async def patch_switch_password(password: str, new_password: str, response: Response,
                                session: SessionDep, payload: str = Depends(jwt_checker)):
    query = await session.execute(
        select(UserModel).filter((UserModel.id == payload["user_id"]))
    )
    user_data = query.scalar_one_or_none()
    if user_data is None or not verify_password(password, user_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password not current")
    user_data.password = hash_password(new_password)
    await session.flush()
    await session.commit()

    response.delete_cookie(key="access_token")
    await delete_user_tokens(session=session, payload=payload)

    return Response(status_code=status.HTTP_205_RESET_CONTENT)


@api_auth_router.delete('/out', status_code=status.HTTP_204_NO_CONTENT)
async def delete_token_database(request: Request, session: SessionDep, payload: str = Depends(jwt_checker)):
    access_token = request.cookies.get("access_token")

    query = await session.execute(
        select(TokenModel).filter((TokenModel.access_token == access_token) & (TokenModel.user_id == payload["user_id"]))
    )
    token_to_delete = query.scalar_one_or_none()

    if token_to_delete:
        await session.delete(token_to_delete)
        await session.flush()
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access token not found")


@api_auth_router.get('/tokens', status_code=status.HTTP_200_OK)
async def get_info_database(session: SessionDep, payload: str = Depends(jwt_checker)):
    query = await session.execute(
        select(TokenModel).filter(TokenModel.user_id == payload["user_id"])
    )

    user_data_tokens = query.scalars().all()
    only_user_tokens = [user_data_token.access_token for user_data_token in user_data_tokens]

    return only_user_tokens


@api_auth_router.delete('/out_all', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_tokens(session: SessionDep, payload: str = Depends(jwt_checker)):
    query = await session.execute(
        select(TokenModel).filter(TokenModel.user_id == payload["user_id"])
    )
    user_data_tokens = query.scalars().all()
    for user_data_token in user_data_tokens:
        await session.delete(user_data_token)
    await session.flush()
    await session.commit()
