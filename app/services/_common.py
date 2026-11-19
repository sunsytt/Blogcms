from pydantic import BaseModel


def apply_updates(entity: object, data: BaseModel, nullable: tuple[str, ...] = ()) -> None:
    """Aplica solo los campos enviados. Un null explícito se ignora salvo en campos anulables."""
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None and field not in nullable:
            continue
        setattr(entity, field, value)
