import re
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.match(r"^\d{10}$", value):
            raise ValueError("Phone must contain exactly 10 digits.")
        super().__init__(value)

# Клас для зберігання дня народження.
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")  # Перевірка формату
            self.value = value  # Зберігаємо як рядок
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone): 
        self.phones.append(Phone(phone))

    def remove_phone(self, phone): 
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone): 
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Old phone not found.")

    def find_phone(self, phone): 
        return next((p for p in self.phones if p.value == phone), None)
    
    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday is already set.")
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday_str = f", Birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name): 
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"No contact named {name}")
        
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_date.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= 7:
                    greeting_date = birthday_this_year
                    if greeting_date.weekday() == 5:  # Якщо субота
                        greeting_date += timedelta(days=2)
                    elif greeting_date.weekday() == 6:  # Якщо неділя
                        greeting_date += timedelta(days=1)
                    upcoming_birthdays.append({"name": record.name.value, "birthday": greeting_date.strftime("%d.%m.%Y")})
        return upcoming_birthdays

    def __str__(self):
        return "\n".join([str(record) for record in self.data.values()])

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This contact does not exist." 
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter the argument for the command."
        except TypeError: # тепер помилку TypeError перехоплює
            return "Invalid input. Please check your data and try again." 
    return inner

def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args

@input_error 
def add_contact(args, book: AddressBook):
    name, phone = args[0], args[1] if len(args) > 1 else None  # Перевіряємо, чи є телефон
    
    record = book.find(name)
    message = "Contact updated."
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    
    if phone:
        record.add_phone(phone)
    
    return message

@input_error 
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone updated for contact {name}."
    return "This contact does not exist." 

@input_error
def show_phone(args, book: AddressBook):
    if not args:
        return "Enter a contact name."
    name = args[0]
    record = book.find(name)
    if record:
        return f"Phones for {name}: {', '.join(p.value for p in record.phones)}"
    return "This contact does not exist."

@input_error
def delete_contact(args, book: AddressBook):
    if not args:
        return "Enter a contact name to delete."
    name = args[0]
    book.delete(name)
    return f"Contact {name} deleted."

def show_all(book: AddressBook):
    if not book.data:
        return "No contacts saved."
    return str(book)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for contact {name}."
    return "This contact does not exist."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"Birthday of {name}: {record.birthday.value.strftime('%d.%m.%Y')}"
    return "No birthday found for this contact."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join([f"{entry['name']}: {entry['birthday']}" for entry in upcoming])

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    commands = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "birthday": show_birthday,
        "add-birthday": add_birthday,
        "birthdays": birthdays,
    }

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            print("Please enter a valid command.")
            continue

        command, args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command in commands:
            print(commands[command](args, book))
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
