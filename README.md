# File Importer

This package will allow you to accept an API request with transactional data and another API request to query that data.


## Installation

Run the installation file to set up the project:

    ./scripts/install.sh


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

    Success refers to the attempting to save data. if ignore_errors = Dalse (the default position),
    then success will be Dalse as soon as there is one error. With ignore_errors = True, the import
    service will attempt to import all valid transactions and return True if it doesn't encounter
    any errors even if there weren't actually any valid transactions.

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
        [transaction date, country, currency, transaction type, net amount, VAT amount,
         Net amount (EUR), VAT amount (EUR)]

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

I think it's especially important not to start trying to handle edge cases manually, eg. if the API expects a row to say either "Purchase" or "Sale", then accepting a different casing or unnecessary white space may be deemed to be an acceptable compromise but catering for misspellings is a doomed path with every option have an almost limitless variety in possible misspellings, putting an excessive burden on the dev team to maintain a list of corrections, eg. co-ercing all "sele", "seel", "sell", "sales", "slaes", etc. as "Sale".

Be rigid but also be clear about why the data is failing to validate.


### All or Nothing... Where Sensible

Certain tasks can be reasonably batched and separated but other tasks are better left either committing to a complete treatment or not.

In this case, I though the initial saving of the data was an "all or nothing" approach - either all of the data should validate or none of it should. The pain to having to worry about a partially imported file and then trying to separate the imported rows from those that need to be fixed can be non-trivial. That said, for the sake of this test, this API will allow the importing of all valid rows and simply ignoring all invalid rows.

In spite of that, the conversion of amounts to Euros can be done as a separate task. Because it depends on a matching country, a separate task will exist that will update all entries where possible. This separation allows us to expose another API route that will re-run just the amount conversions to Euros on all outstanding transactions, with time for the user to fix the entries that don't have countries usable by the conversion API.


### Financial Sensibilities

Transactions can be either positive and negative reflecting incoming and outgoing money or balances. Whether an amount is considered positive or negative depends on context (bank balance, debtors, vat owed, etc) but for the sake of this test, Sales and VAT on Sales will be considered positive (income received) and Payments and VAT on Payments will be considered negative.


### Improvement Opportunities

This test is by no means perfect but should hopefully show you what I can do. That said, where I'd take this further if it were to go into production:
- Small refactoring of templates in the client - using the Django template inheritance structure is definitely preferred
- Being able to download the list of query results (as csv or in excel format)
