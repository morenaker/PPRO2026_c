class DomainError(Exception):
    """Porušení obchodního pravidla. Web vrstva z něj udělá srozumitelnou hlášku."""


class DuplicatePatientError(DomainError):
    def __init__(self, existing_id: int) -> None:
        super().__init__("Pacient s tímto číslem pojištěnce už v evidenci je.")
        self.existing_id = existing_id
