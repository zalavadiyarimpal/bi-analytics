
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, model_validator, Field

from rest_framework.exceptions import ValidationError as DRFValidationError


class JoinConfig(BaseModel):
    type: str
    table: str
    on: List[str]


class DataSource(BaseModel):
    type: str
    connection_id: str
    table: str
    joins: List[JoinConfig] = Field(default_factory=list)
    where: Optional[str] = None



class DimensionField(BaseModel):
    type: str
    field: Optional[str] = None
    expression: Optional[str] = None
    alias: str
    agg: Optional[str] = None

    @model_validator(mode="after")
    def validate_fields(cls, values):
        typ = values.type
        field = values.field
        expr = values.expression
        agg = values.agg

        if typ == "column" and not (field or expr):
            raise ValueError("For 'column' type, 'field' or 'expression' is required.")
        if typ == "agg":
            if not field or not agg:
                raise ValueError("For 'agg' type, 'field' and 'agg' are required.")
        return values



class Dimensions(BaseModel):
    rows: List[DimensionField]
    columns: List[DimensionField] = Field(default_factory=list)
    measures: List[DimensionField] = Field(default_factory=list)


class FilterCondition(BaseModel):
    operator: str
    value: Union[str, int, List[Any]]


class SortField(BaseModel):
    field: str
    order: str  # expected "asc" or "desc"


class ReportConfig(BaseModel):
    report_name: str
    data_source: DataSource
    dimensions: Dimensions
    filters: Dict[str, FilterCondition] = Field(default_factory=dict)
    group_by: List[str] = Field(default_factory=list)
    sort_by: List[SortField] = Field(default_factory=list)
    limit: Optional[int] = None

def validateReportConfig(config):
    # return ReportConfig(**config)  # Pydantic validation
    try:
        return ReportConfig(**config)  # Pydantic validation
    except PydanticValidationError as e:
        raise DRFValidationError(detail=e.errors())  # convert to DRF

