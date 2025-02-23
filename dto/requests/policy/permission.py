from typing import Optional
from pydantic import BaseModel
from dto.resources.policy.permission import PermissionResourceDTO


class CreatePermissionRequestDTO(BaseModel):
    name: str
    description: str
    cipher: str

    def to_dto(self, created_by: int) -> PermissionResourceDTO:
        return PermissionResourceDTO(
            name=self.name,
            description=self.description,
            cipher=self.cipher,
            created_by=created_by
        )


class UpdatePermissionRequestDTO(BaseModel):
    name: Optional[str]
    description: Optional[str]
    cipher: Optional[str]

    def to_dto(self, permission_model: PermissionResourceDTO, updated_by: int):
        permission_model.name = self.name if permission_model.name is None else permission_model.name
        permission_model.description = self.description if permission_model.description is None \
            else permission_model.description
        permission_model.cipher = self.cipher if permission_model.cipher is None else permission_model.cipher
        permission_model.updated_by = updated_by
