"""Exceptions für die Service-Schicht."""


class EmailExistsError(Exception):
    """Exception, falls eine Emailadresse bereits existiert."""

    def __init__(self, email: str) -> None:
        """Initialisierung mit der bereits vorhandenen Emailadresse.

        :param email: Bereits vorhandene Emailadresse
        """
        super().__init__(f"Die Emailadresse {email} existiert bereits.")
        self.email = email
