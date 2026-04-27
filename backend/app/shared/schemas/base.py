"""
Base schemas avec configuration commune
"""
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Schema de base pour tous les schemas Pydantic
    
    Configuration commune :
    - from_attributes: Permet de créer depuis ORM models
    - validate_assignment: Valide lors de modifications
    - str_strip_whitespace: Trim les strings
    """
    
    model_config = ConfigDict(
        from_attributes=True,  # Permet User.model_validate(db_user)
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )