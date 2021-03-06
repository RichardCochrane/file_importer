# File Importer

This package will allow you to accept an API request with transactional data and another API request to query that data.


## Installation

Run the installation file to set up the project:

    ## Clone the repo
    git clone git@github.com:RichardCochrane/file_importer.git

    ## Install the actual app
    (from the root folder)
    ./scripts/install.sh
    cp dev.env .env

    ## Get the database migrated to the latest schema
    (from the file_importer folder)
    ../venv/bin/python manage.py migrate


## Running the app

This app will run on port 8080 and can be run using the command:

    ./run_server.sh


## API Calls

### Security

The contents of API requests must be secured through a security hash that requires the ownership of a particular secret. Failure to present a valid security hash will result in a 403 forbidden error response.


### Heartbeat

A standard heartbeat API call that monitoring services can use to determine that the API is, in fact, still running. Will simply return a 200 response with the text OK.

### Receive Transactional Data

This will accept a POST stream of data in the JSON format, validate and either save the data (if it is all valid) or return an error code with a list of validation errors.

Parameters:
- api_partner_id: a unique ID that identifies the calling party
- transaction_data: a list of lists each containing the transaction data in the order:
                    transaction date, transaction type, country, currency, net amount, VAT amount
- ignore_errors: a boolean value that, when False, will halt the import of data if there are any
                 errors present and, when True, will allow the importing of all valid transactions
                 (default False)
- ignore_first_row: a boolean value to indicator whether the first row should be ignored (as with
                    headings)

URL:
[HOST URL]/api/v1/transactions/import

#### Response (successful attempt)

Status: 200

Content: JSON structure:

    {
        "success": [True/False],
        "message": summary message,
        "errors": [a list of validation errors in the form: [row number, value, error description]]
    }

Success refers to the attempting to save data. if ignore_errors = Dalse (the default position), then success will be Dalse as soon as there is one error. With ignore_errors = True, the import service will attempt to import all valid transactions and return True if it doesn't encounter any errors even if there weren't actually any valid transactions.

Errors will be a list of errors in validating the file whatever the value of ignore_errors.

#### Response (invalid security hash)

Status: 403

Content: None


### Query Transactional Data

This will accept a GET request to query the transactional data saved on the system.

Parameters:
- api_partner_id: a unique ID that identifies the calling party
- country_code: the 2-letter abbreviation of the country
- query_date: the date requested in the format: YYYY/MM/DD

URL:
[HOST URL]/api/v1/transactions/query

#### Response (valid request)

Status: 200

Content: JSON structure:

    {
        'transactions': [list of transactions]
    }

Each transaction is a list with the following data:
    [transaction date, country, currency, transaction type, net amount, VAT amount, Net amount (EUR), VAT amount (EUR)]

#### Response (invalid request)

Status: 400

Content: JSON structure:

    {'errors': [list of errors]}


#### Response (invalid security hash)

Status: 403

Content: None


## Assumptions

### Security is Key

To prevent unauthorised use of the API and protect the integrity of our data, it is necessary to safeguard the contents of every GET and POST request. This will be done with a secret key that each API partner has access to.


### Strict Validation is Better for Everyone

Ideally, you want to be as permissable as you can be (accepting and working with quirks in the data) but you have to be careful not to get too clever, allowing users to submit any variety of sloppy data. I think it enforces a healthier API if the rules are rigid but clear.

I think it's especially important not to start trying to handle edge cases manually, eg. if the API expects a row to say either "Purchase" or "Sale", then accepting a different casing or unnecessary white space may be an acceptable compromise but catering for misspellings puts an excessive burden on the dev team to maintain a list of corrections, eg. co-ercing all "sele", "seel", "sell", "sales", "slaes", etc. as "Sale".

Be rigid but also be clear about why the data is failing to validate.


### All or Nothing... Where Sensible

Certain tasks can be reasonably batched and separated but other tasks are better left either committing to a complete treatment or not.

In this case, I thought the initial saving of the data was an "all or nothing" approach - either all of the data should validate or none of it should. The pain to having to worry about a partially imported file and then trying to separate the imported rows from those that need to be fixed can be non-trivial. That said, for the sake of this test, this API will allow the importing of all valid rows and simply ignoring all invalid rows.

The conversion of amounts to Euros, however, can be done as a separate task. Because it depends on a matching currency, a separate task will update all entries where possible allowing the task to be run again when the matching data have improved.


### Financial Sensibilities

Transactions can be either positive and negative reflecting incoming and outgoing cash flow. Whether an amount is considered positive or negative depends on context (bank balance, debtors, vat owed, etc) but for the sake of this test, Sales and VAT on Sales will be considered positive (income received) and Payments and VAT on Payments will be considered negative.


### Improvement Opportunities

This test is by no means perfect but should hopefully show you what I can do. That said, where I'd take this further if it were to go into production:
- Small refactoring of templates in the client - using the Django template inheritance structure is definitely preferred
- Being able to download the list of query results (as csv or in excel format)
- Automated tests should definitely be present in anything actually running in production


## Scaling for Future Growth

My separation of file import from Euro conversions would definitely help to allow scaling horizontally at either one of those parts without affecting the other. I have a basic chunking available, but commented out, that would commit the transactions in batches instead of individually. For the number of transactions here, commit invidual database inserts is feasible but dealing with millions of records would require optimisation in how the database connections are used.

I would a NO-SQL databaes to cache the exchange rates so that it's only ever done once a day.


## Screenshots

The File Importer Client has a folder with [screenshots](https://github.com/RichardCochrane/file_importer_client/tree/main/screenshots) that show you HOW the pages should look, in the event that you are not able to run my code. I've cloned the repos and run through the installation twice so it should work and I'm happy to help fix any issues that arise when installing or running the apps.

## An Apology

I glossed over the requirement to use the Django REST framework, instead cobbling my own API. This was not intentional - I believe that using community-developed, well-trusted software, like the Django REST framework, is absolutely a better way to go over hand-coding your own solution but it was a detail I missed until it was too late to go back and rewrite the API to use it. That said, I hope that what I've done demonstrates mastery of this.
