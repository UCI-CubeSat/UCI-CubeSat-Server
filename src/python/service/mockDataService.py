from faker import Faker

Faker.seed()
fake = Faker()


def generateTimestamp() -> fake.future_datetime:
    """
    Returns: any future datetime(year, month, day, hour, minute, second)
    """
    return fake.future_datetime()


def generateTemperature() -> fake.pyfloat:
    """
    Returns: any float between -40°C to +105°C (AEC-Q100 Level 2)
    """
    return fake.pyfloat(min_value=-40, max_value=105)


def generateVoltage() -> fake.pyfloat:
    """
    Returns: any float between -5V to +5V
    """
    return fake.pyfloat(min_value=-5, max_value=5)


def generateLngLat() -> dict[str, fake.pydecimal]:
    """
    Returns: any valid {lng: Decimal('13.4134995'),
                lat: Decimal('13.4134995')}
    """
    return dict(lng=fake.longitude(),
                lat=fake.latitude())


def generateLocation() -> dict[str, fake.pydecimal | str]:
    """

    Returns: any valid {lng: Decimal('13.4134995'),
                lat: Decimal('13.4134995')},
                city: "Irvine",
                country: "US",
                timezone: "America/Los_Angeles"}
    """
    location: (str, str, str, str, str) = fake.local_latlng()
    return dict(lng=location[1],
                lat=location[0],
                city=location[2],
                country=location[3],
                timezone=location[4])


def generateAltitude():
    pass


def generateMessage():
    pass


def generateAscii():
    pass


def generateDownLinkStatus():
    pass


def generateUpLinkStatus():
    pass


def generateDetumblingStatus():
    pass


def generateMagnetorquerStatus():
    pass


def generateEpsStatus():
    pass


def generateGyroStatus():
    pass


def generateAntennaStatus():
    pass


if __name__ == "__main__":
    for funcName in dir():
        if funcName[:len("generate")] != "generate":
            continue

        try:
            fakeData = locals()[funcName]()
        except KeyError:
            continue

        if not fakeData:
            continue

        print(f"{funcName} {fakeData}")


