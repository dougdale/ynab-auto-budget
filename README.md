# ynab-auto-budget
Automatically create monthly budget amounts based on user budget template using YNAB API

## Credentials File
The YNAB API credentials file is, by default expected to be named ynab_credentials.json in a '.ynab' directory under the user's home directory.

The format is as follows:
```json
{
    "key": "<user's API key>",
    "prefix": "Bearer"
}
```

See the [YNAB API documentation](https://api.youneedabudget.com/) for details about generating the key.
