# FetchPoints

## _Points System for Fetch_

A system to gain or utilize points via transactions

## Features

- Commit (multiple) transactions
- Give points to payers
- Use points (optional: from certain payers)
- Return a list of points from payers

## Tech

FetchPoints uses a number of open source projects to work properly:

- [Flask] - Micro Web Framework which utilizes Python 
- [PyMongo] - Establishes connection with MongoDB via Python

## Installation

FetchPoints requires Flask and PyMongo to run.

Install the dependencies and start the server.

```sh
pip install pymongo Flask
```

## Usage
Run app.py to start the server up.
| Route              | Required                     |
| ------------------ | ---------------------------- |
|`/api/spend_points` | `int` Amount                 |
|`/api/give_points`  | `int` Amount, `string` payer |
|`/api/balance`      | `None`                       |

`api/spend_points` - Spends points based on amount given. 
`api/give_points` - Get points from payer based on amount
`api/balance` - Returns the amount of points from each payer


## Testing
To run the test cases, you have to run the app.py first then run the test.py. 
`WARNING`: Testing resets the database so only do this during development.

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
   [Flask]: https://flask.palletsprojects.com/en/2.0.x/
   [PyMongo]: https://pymongo.readthedocs.io/en/stable/
   
   [MarkDownCredit]: dillinger.io
