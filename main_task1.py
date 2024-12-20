from collections import UserDict
from datetime import datetime, date, timedelta


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "The contact exists"
        except ValueError:
            return "Please enter the correct arguments"
        except IndexError:
            return "No such contacts"

    return inner


# Парсинг введеної строки
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    # Валідація номеру телефону
    def __init__(self, phone_number):
        if not (len(phone_number) == 10 and phone_number.isdigit()):
            raise ValueError('Number is not correct!')
        super().__init__(phone_number)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
            super().__init__(self.value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Метод для додавання номеру телефону
    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    # Метод для видалення номеру телефону
    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)

    # Метод для редагування номеру телефону
    def edit_phone(self, old_phone_number, new_phone_number):
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = Phone(new_phone_number).value
                break
        else:
            raise ValueError('Number is not exist')

    # Метод для пошуку об'єктів Phone
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    # Метод який додає дату народження до контакту
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # Магічний метод для красивого виводу об’єкту класу
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(phone.value for phone in self.phones)}, Birthday:{self.birthday}"


class AddressBook(UserDict):
    # Метод який додає запис до self.data
    def add_record(self, record_name):
        self.data[record_name.name.value] = record_name

    # Метод який знаходить запис за ім'ям.
    def find(self, find_name):
        return self.data.get(find_name)

    # Метод який видаляє запис за ім'ям.
    def delete(self, delete_name):
        if delete_name in self.data:
            del self.data[delete_name]

    # Метод який визначає контакти, у яких день народження припадає вперед на 7 днів
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for user in self.data.values():
            if user.birthday:
                birthday_this_year = user.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = user.birthday.value.replace(year=today.year + 1)
                if 0 <= (birthday_this_year - today).days <= days:
                    if birthday_this_year.weekday() >= 5:
                        days_ahead = 0 - birthday_this_year.weekday()
                        if days_ahead <= 0:
                            days_ahead += 7
                        birthday_this_year += timedelta(days=days_ahead)
                    upcoming_birthdays.append(
                        {"name": user.name.value, "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")})
        return upcoming_birthdays

    # Магічний метод для красивого виводу об’єктів класу
    def __str__(self):
        if not self.data:
            return "Address Book is empty."

        result = "Address Book:\n"
        result += "-" * 40 + "\n"
        for name, record in self.data.items():
            result += f"{record}\n"
            result += "- " * 20 + "\n"
        return result


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


# Зміна контакту
@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        if record.find_phone(old_phone):
            record.edit_phone(old_phone, new_phone)
            return "Contact updated."
        else:
            return f"Number {old_phone} is not {name}'s phone number!"
    else:
        return f'Contact {name} is not in the list'


# Показ контакту
@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return record
    else:
        return f'Contact {name} is not in the list'


# Виведення всих номерів
def show_all(book: AddressBook):
    if not book:
        return "Contact list is empty"
    else:
        return book


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return f"Contact {name} is not in the list!"


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return f'Contact: {name}, Birthday:{record.birthday}'
    else:
        return f"Contact {name} is not in the list!"


@input_error
def birthdays(book: AddressBook):
    if not book:
        return "Contact list is empty"
    else:
        return book.get_upcoming_birthdays()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == '__main__':
    main()