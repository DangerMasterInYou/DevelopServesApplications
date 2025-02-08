from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import datetime, date


class LoginRequestApiAuthDTO(BaseModel):
    username: str = Field(..., min_length=7)
    password: str = Field(..., min_length=8)

    @model_validator(mode='before')
    def validate_username(cls, values):
        username = values.get('username')

        if not username.isalpha():
            raise ValueError('Username must contain only Latin letters.')

        if not username[0].isupper():
            raise ValueError('Username must start with an uppercase letter.')

        return values

    @model_validator(mode='before')
    def validate_password(cls, values):
        password = values.get('password')

        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit.')

        if not any(not char.isalnum() for char in password):
            raise ValueError('Password must contain at least one special character.')

        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter.')

        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter.')

        return values


class RegistrationRequestApiAuthDTO(BaseModel):
    username: str = Field(..., min_length=7)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    c_password: str = Field(..., min_length=8)
    birthday: str = Field(..., pattern=r'\d{4}-\d{2}-\d{2}')

    @model_validator(mode='before')
    def validate_username(cls, values):
        username = values.get('username')

        if not username.isalpha():
            raise ValueError('Username must contain only Latin letters.')

        if not username[0].isupper():
            raise ValueError('Username must start with an uppercase letter.')

        return values

    @model_validator(mode='before')
    def validate_email(cls, values):
        return values

    @model_validator(mode='before')
    def validate_password(cls, values):
        password = values.get('password')

        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password):
            raise ValueError('Password must contain at least one digit.')
        if not any(not char.isalnum() for char in password):
            raise ValueError('Password must contain at least one special character.')
        if not any(char.isupper() for char in password):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password):
            raise ValueError('Password must contain at least one lowercase letter.')

        return values

    @model_validator(mode='before')
    def validate_c_password(cls, values):
        if 'password' in values and values['c_password'] != values['password']:
            raise ValueError('c_password must match the password.')
        return values

    @model_validator(mode='before')
    def validate_birthday(cls, values):
        birthday_str = values.get('birthday')
        birth_date = datetime.strptime(birthday_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 14:
            raise ValueError('User must be at least 14 years old.')
        return values
