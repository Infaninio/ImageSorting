import getpass
import sqlite3

from werkzeug.security import generate_password_hash


def main():
    """Create Image Sorting database."""
    # Create a SQLite database with name 'ImageSorting.sqlite'
    conn = sqlite3.connect("ImageSorting.sqlite")
    c = conn.cursor()

    # Load the schema.sql file to create tables in the database
    with open("./Database/schema.sql", mode="r") as f:
        c.executescript(f.read())

    # Ask the user to provide a password for the admin user
    while True:
        print("Set the password for the 'Admin' user.")

        # Prompt the user to enter the password twice without displaying it
        password = getpass.getpass(prompt="Enter password: ")
        confirm_password = getpass.getpass(prompt="Confirm password: ")

        if password != confirm_password:
            print("Passwords do not match. Please try again.\n")
        elif len(password) == 0:
            print("Password cannot be empty. Please try again.\n")
        else:
            break

    # Insert the Admin user into the database
    c.execute(
        "INSERT INTO user (email, password, create_collection) VALUES (?, ?, ?)",
        ("Admin", generate_password_hash(password=password), True),
    )

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database created successfully.")


if __name__ == "__main__":
    main()
