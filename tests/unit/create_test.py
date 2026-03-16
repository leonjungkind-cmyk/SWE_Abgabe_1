# ruff: noqa: S101, D103, ARG005
# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Unit-Tests für find_by_id() von PatientService."""

from copy import deepcopy
from datetime import date
from typing import TYPE_CHECKING

from pytest import fixture, mark, raises

from patient.entity import Adresse, Familienstand, Geschlecht, Patient
from patient.service import EmailExistsError, UsernameExistsError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@fixture
def session_mock(mocker: MockerFixture):
    session = mocker.Mock()
    # Patching von "with Session() as session:" in patient_write_service.py
    mocker.patch(
        "patient.service.patient_write_service.Session",
        return_value=mocker.MagicMock(
            __enter__=lambda self: session,
            __exit__=lambda self, exc_type, exc, tb: None,
        ),
    )
    return session


@mark.unit
@mark.unit_create
def test_create(
    patient_write_service, session_mock, keycloak_admin_mock, mocker
) -> None:
    # Arrange
    email = "mock@email.test"
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        patient_id=None,
        patient=None,
    )
    patient = Patient(
        id=None,
        email=email,
        nachname="Mocktest",
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse.patient = patient
    patient_db_mock = deepcopy(patient)
    generierte_id = 1
    patient_db_mock.id = generierte_id
    patient_db_mock.adresse.id = generierte_id

    # Patch fuer KeycloakAdmin.get_user_id() und KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None
    keycloak_admin_mock.get_users.return_value = []

    # session.scalar(select(func.count()).where(Patient.email == email)
    session_mock.scalar.return_value = 0
    session_mock.add.return_value = None

    def flush_side_effect(objects=None):
        for obj in objects or []:
            obj.id = generierte_id  # Emulation: generierter PK in session.flush()

    session_mock.flush.side_effect = flush_side_effect

    # Patch fuer die Funktion send_mail
    mocker.patch("patient.service.patient_write_service.send_mail", return_value=None)

    # Act
    patient_dto = patient_write_service.create(patient=patient)

    # Assert
    assert patient_dto.id == generierte_id


@mark.unit
@mark.unit_create
def test_create_username_none(patient_write_service) -> None:
    # Arrange
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        patient_id=None,
        patient=None,
    )
    patient = Patient(
        id=None,
        email="mock@email.test",
        nachname="Mocktest",
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username=None,
        adresse=adresse,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse.patient = patient

    # Act
    with raises(ValueError) as err:
        patient_write_service.create(patient=patient)

    # Assert
    assert err.type is ValueError


@mark.unit
@mark.unit_create
def test_create_username_exists(patient_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        patient_id=None,
        patient=None,
    )
    patient = Patient(
        id=None,
        email=email,
        nachname="Mocktest",
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse.patient = patient

    # Patch fuer KeycloakAdmin.get_user_id()
    user_id = "12345678-1234-1234-1234-123456789012"
    keycloak_admin_mock.get_user_id.return_value = user_id
    keycloak_admin_mock.get_users.return_value = []

    # Act
    with raises(UsernameExistsError) as err:
        patient_write_service.create(patient=patient)

    # Assert
    assert err.type is UsernameExistsError


@mark.unit
@mark.unit_create
def test_create_email_exists(patient_write_service, keycloak_admin_mock) -> None:
    # Arrange
    email = "mock@email.test"
    adresse = Adresse(
        id=999,
        plz="11111",
        ort="Mockort",
        patient_id=None,
        patient=None,
    )
    patient = Patient(
        id=None,
        email=email,
        nachname="Mocktest",
        kategorie=1,
        has_newsletter=True,
        geburtsdatum=date(2025, 1, 31),
        geschlecht=Geschlecht.MAENNLICH,
        familienstand=Familienstand.LEDIG,
        homepage="https://www.test.de",
        username="mocktest",
        adresse=adresse,
        fachaerzte=[],
        rechnungen=[],
    )
    adresse.patient = patient

    # Patch fuer KeycloakAdmin.get_users()
    keycloak_admin_mock.get_user_id.return_value = None  # sonst UsernameExistsError
    keycloak_admin_mock.get_users.return_value = [
        {"id": "12345678-1234-1234-1234-123456789012", "email": email}
    ]

    # Act
    with raises(EmailExistsError) as err:
        patient_write_service.create(patient=patient)

    # Assert
    assert err.type is EmailExistsError
