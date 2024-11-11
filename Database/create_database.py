import sqlite3

# Create a SQLite database with name 'ImagSorting'
conn = sqlite3.connect("ImageSorting.sqlite")
c = conn.cursor()

# Load the schema.sql file to create tables in the database
with open("./Database/schema.sql", mode="r") as f:
    c.executescript(f.read())

# Commit the changes and close the connection
conn.commit()
conn.close()
