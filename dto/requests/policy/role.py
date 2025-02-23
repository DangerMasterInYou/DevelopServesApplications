from typing import Optional
from pydantic import BaseModel
from dto.resources.policy.role import RoleResourceDTO


class CreateRoleRequestDTO(BaseModel):
    name: str
    description: str
    cipher: str

    def to_dto(self, created_by: int) -> RoleResourceDTO:
        return RoleResourceDTO(
            name=self.name,
            description=self.description,
            cipher=self.cipher,
            created_by=created_by
        )


class UpdateRoleRequestDTO(BaseModel):
    name: Optional[str]
    description: Optional[str]
    cipher: Optional[str]

    def to_dto(self, role_model: RoleResourceDTO, updated_by: int):
        role_model.name = self.name if role_model.name is None else role_model.name
        role_model.description = self.description if role_model.description is None else role_model.description
        role_model.cipher = self.cipher if role_model.cipher is None else role_model.cipher
        role_model.updated_by = updated_by
