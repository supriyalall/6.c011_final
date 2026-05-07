# BigCodeBench-Hard Baseline Failure Analysis

Source files: `baseline_detail.json`, `plan_then_code_detail.json`, and cached BigCodeBench-Hard task metadata.

## Outcome Counts

| Outcome | Count | Share of 148 tasks |
|---|---:|---:|
| Both baseline and plan-then-code pass | 29 | 19.6% |
| Baseline passes, plan-then-code fails | 9 | 6.1% |
| Baseline fails, plan-then-code passes | 8 | 5.4% |
| Both fail | 102 | 68.9% |

Baseline fails on **110 / 148** BCB-Hard tasks (74.3%).
Plan-then-code fixes **8** of those failures, but **102** remain unsolved by both strategies.

## Baseline Failure Modes

| Failure mode | Count |
|---|---:|
| test assertion / hidden mismatch | 90 |
| missing dependency | 13 |
| timeout | 6 |
| runtime exception | 1 |

## Where the Baseline Fails

| Task pattern | Baseline failures | Fixed by plan-then-code | Still both fail |
|---|---:|---:|---:|
| plotting / visualization | 41 | 2 | 39 |
| data wrangling / tables | 33 | 2 | 31 |
| general library/API use | 13 | 3 | 10 |
| web / file I/O | 12 | 0 | 12 |
| text processing | 4 | 1 | 3 |
| date/time handling | 3 | 0 | 3 |
| image / OCR processing | 2 | 0 | 2 |
| structured parsing | 1 | 0 | 1 |
| ML/statistics | 1 | 0 | 1 |

## Baseline Failures Fixed by Plan-then-code

| task_id | Pattern | Prompt summary |
|---|---|---|
| BigCodeBench/368 | general library/API use | Moves a random file from the source directory to the specified destination directory. The function should output with: str: The name of the file mo... |
| BigCodeBench/401 | text processing | Initializes a Flask-Mail instance for sending emails using the generated Flask application with the specified app_name. Note that: The details of t... |
| BigCodeBench/461 | general library/API use | Executes a given bash script and returns the CPU and memory usage of the script's process. This function checks whether the script path exists, the... |
| BigCodeBench/618 | plotting / visualization | Generate and visualize a Pandas DataFrame of the results of football matches for multiple teams 'Team' with random goals 'Goals' and penalties 'Pen... |
| BigCodeBench/760 | data wrangling / tables | Creates a random DataFrame with 100 records. Each record consists of an ID (ranging from 1 to 100), Name (randomly selected from provided lists of ... |
| BigCodeBench/765 | general library/API use | Process files from a dictionary by checking if the file exists, and if it has content, then copies it to a target directory. The function should ou... |
| BigCodeBench/870 | data wrangling / tables | Calculate the mean of numerical values in each position across tuples in a list. Non-numeric values are ignored, and means are computed only from a... |
| BigCodeBench/917 | plotting / visualization | Forecasts the share closing prices for the next 7 days using the ARIMA model and plots the forecast. The function should output with: Tuple[List[fl... |

## Representative Persistent Baseline Failures

| task_id | Pattern | Failure mode | Prompt summary |
|---|---|---|---|
| BigCodeBench/100 | plotting / visualization | timeout | Generates a plot of random time series data for the past 30 days with reproducibility controlled by an optional seed parameter. The plot is styled ... |
| BigCodeBench/1003 | data wrangling / tables | test assertion / hidden mismatch | Fetches and parses an XML file from a specified URL, then converts it into a Pandas DataFrame. # Example with an invalid XML structure >>> df = tas... |
| BigCodeBench/1004 | plotting / visualization | test assertion / hidden mismatch | Downloads a text file from a specified URL, processes the text to count the frequency of each word, and then plots a bar chart showing the ten most... |
| BigCodeBench/1008 | data wrangling / tables | test assertion / hidden mismatch | Extracts and converts data from a specified HTML table based on the given 'table_id' on a webpage into a Pandas DataFrame. If the table is present ... |
| BigCodeBench/101 | plotting / visualization | test assertion / hidden mismatch | Draw the correlation heatmap of the Boston Housing dataset using Seaborn, with an option to save it to a specified file. The function should raise ... |
| BigCodeBench/1012 | web / file I/O | test assertion / hidden mismatch | Downloads and extracts a zip file from a specified URL. Note that: the status message will contain "Error" when: Network-related exceptions are rai... |
| BigCodeBench/1015 | data wrangling / tables | test assertion / hidden mismatch | This function parses HTML table data from a specified URL or local file and stores it into an SQLite database. The function handles different scena... |
| BigCodeBench/1019 | image / OCR processing | missing dependency | Opens an image file, extracts text using OCR, and converts the text encoding, with a fallback to image comment processing. The function should rais... |
| BigCodeBench/1039 | web / file I/O | test assertion / hidden mismatch | This function secures a client socket using SSL/TLS and sends back the SHA256 hash of a file requested by the client. Note that: This function assu... |
| BigCodeBench/1040 | date/time handling | timeout | Run a non-blocking echo server that appends the server's current time to received data and sends it back to the client, while handling exceptional ... |
| BigCodeBench/1042 | text processing | test assertion / hidden mismatch | Receive a message from a client socket and send it as an email via an SMTP server. Note that: Requires a working internet connection and access to ... |
| BigCodeBench/108 | plotting / visualization | test assertion / hidden mismatch | Decomposes a time series in the 'value' column of a DataFrame into trend, seasonality, and residuals. The function should raise the exception for: ... |
| BigCodeBench/1085 | plotting / visualization | test assertion / hidden mismatch | Analyzes the frequency of words in a given text after lowercasing, removing punctuation, splitting into words, and plots the top 10 most common wor... |
| BigCodeBench/1124 | web / file I/O | test assertion / hidden mismatch | Extracts a URL from a given string and retrieves the title of the web page from that URL. If no valid URL is found, or the URL does not result in a... |
| BigCodeBench/1129 | web / file I/O | test assertion / hidden mismatch | Parses a JSON string to find a URL associated with a specified key, downloads the file from the URL, and saves it with a timestamped filename. The ... |
| BigCodeBench/1137 | web / file I/O | test assertion / hidden mismatch | Extracts phone numbers from a given URL or local file and saves them to a specified file in JSON format. The function should output with: list: A l... |
| BigCodeBench/120 | data wrangling / tables | test assertion / hidden mismatch | Generate a pandas Series of random dates within a specified date range, including both start_date and end_date, with an optional seed for reproduci... |
| BigCodeBench/124 | plotting / visualization | test assertion / hidden mismatch | Enhances 'my_list' by appending the number 12, then generates a list of random integers based on the sum of elements in 'my_list', limited by 'size... |
| BigCodeBench/129 | data wrangling / tables | test assertion / hidden mismatch | Scrape the first table from a web page and extract data into a Pandas DataFrame. This function scrapes the first table found on the specified web p... |
| BigCodeBench/13 | web / file I/O | test assertion / hidden mismatch | Download all files from a specific directory on an FTP server using wget in a subprocess. Args: ftp_server (str): The FTP server address. Default i... |

