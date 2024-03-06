from contacts.seeds import main as contacts_seeds
from users.seeds import main as user_seeds

def main():
    user_seeds()
    contacts_seeds()

if __name__ == "__main__":
    main()