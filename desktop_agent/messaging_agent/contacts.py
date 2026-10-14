CONTACTS = {
    "sumathi": "+919962796237",
    "arun": "+91XXXXXXXXXX",
    "kumar": "+91XXXXXXXXXX"
}


def get_phone_number(name: str):

    name = name.lower().strip()

    return CONTACTS.get(name)