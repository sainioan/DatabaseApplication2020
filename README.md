#### DatabaseApplication2020
# Book Database
Intermediate Studies Project: Database Application 2020

Simple Book library application written on flask with PostgreSQL database.
The book database is an app that allows users to keep a record of books they would like to read, are currently reading, and have read. 

Published online: 
https://tsoha-books.herokuapp.com/

## Requirements:

Execute the following command to install the necessary libraries:<br />

`pip install -r requirements.txt`

## Features
* Users can login, logout 
* Users can view the current New York Times bestseller list in order to get ideas for books to read in the future.
* Users can read summaries and reviews of several books by search a book by its title or author (provided by New York Times API) to know more about the book.
* Users can enter the books they wish to read to their personal reading list
* Users can enter the books they are currently reading to their currently reading list.
* Users can enter the books they have read to books-read list. In addition, they can write include information, such as a comment,
  and rating from scale 1-5 on each book.
* Users can update the current page number of the books they are currently reading and see the completion percentage on the currently reading list.
* Users can also update summary, genre, and page count fields of a book on the currently reading page.
* Users can delete books from their future reading list as well as from their currently reading list.
* Users can update the comment, rating, genre, and summary fields of a book on their books-read list.
* Users can move books from their future reading list to their currently reading list.
* Users can move books from their currently reading list to their books-read list.
* Users can share their review (including title, author, comment, and rating) of a completed book with the app user community. 
* Users can read book reviews (comments and ratings) shared by app users on the community page.
* Users can view data about the books app users are currently reading and the books they have finished reading on the community page.
* Users can view bookcount per app user on the community page.
* Users can add useful links to the application site. The links are visible to all users on the community page.
* Admin(s) can view the list of all app users.
* Admin(s) can delete users, useful links, and public reviews. 
  

## Heroku Username and Password

**Admin**

        Username: administrator

        Password: admin123

**User**

        Username: Annie1

        Password: secret1
        
## User Guide

- [User Guide](https://github.com/sainioan/DatabaseApplication2020/blob/master/documentation/user_guide.md)

## Database and Create Table Statements 
- [Database](https://github.com/sainioan/DatabaseApplication2020/blob/master/documentation/database_%26_create_table_statements.md)

