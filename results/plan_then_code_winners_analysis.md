Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Total aligned tasks: 312
Outcome group counts:
  ptc_helps: 18
  ptc_hurts: 14
  both_pass: 165
  both_fail: 115

## Mean of each feature, by outcome group (combined HumanEval + BCB-Hard)
| feature | ptc_helps | ptc_hurts | both_pass | both_fail | Cohen_d (helps vs rest) |
|---|---:|---:|---:|---:|---:|
| statement_len_log | 6.244 | 6.541 | 5.890 | 6.484 | +0.13 |
| code_len_log | 6.656 | 6.854 | 6.161 | 6.963 | +0.21 |
| ast_nodes_log | 2.679 | 2.530 | 2.400 | 2.837 | +0.18 |
| num_functions | 1.056 | 1.000 | 1.018 | 1.017 | +0.24 |
| cyclomatic_approx | 1.000 | 1.000 | 1.006 | 1.000 | -0.06 |
| coupling_imports | 1.778 | 2.286 | 0.788 | 3.139 | -0.00 |
| coupling_calls | 0.167 | 0.000 | 0.109 | 0.104 | +0.10 |
| compositionality_steps | 0.444 | 0.357 | 0.376 | 0.313 | +0.13 |
| independence_lexical | 0.278 | 0.571 | 0.248 | 0.313 | -0.02 |

## ptc_helps counts by dataset
  bigcodebench: 8
  humaneval: 10

## ptc_helps tasks (the 18 where decomposition flipped fail to pass)

### BigCodeBench/368 (bigcodebench)
  statement: Moves a random file from the source directory to the specified destination directory. The function should output with:     str: The name of the file moved. Format: 'filename.extension' (e.g., 'file1.txt'). You should write self-contained code starting with: ``` import os impor...
  features: stmt_len_log=5.92 code_len_log=6.89 ast_nodes_log=3.18 num_functions=1 comp_steps=0.0 coupling_imports=3 coupling_calls=0

### BigCodeBench/401 (bigcodebench)
  statement: Initializes a Flask-Mail instance for sending emails using the generated Flask application with the specified app_name. Note that: The details of the email server are retrieved from environment variables. If the variables do not exist, use defaults: 'MAIL_SERVER': 'localhost' ...
  features: stmt_len_log=6.46 code_len_log=6.78 ast_nodes_log=2.56 num_functions=1 comp_steps=0.0 coupling_imports=3 coupling_calls=0

### BigCodeBench/461 (bigcodebench)
  statement: Executes a given bash script and returns the CPU and memory usage of the script's process. This function checks whether the script path exists, then it executes it in a subprocess and uses psutil to monitor the script's process for CPU and memory usage. Note that: CPU usage is...
  features: stmt_len_log=6.95 code_len_log=7.33 ast_nodes_log=3.04 num_functions=1 comp_steps=1.0 coupling_imports=4 coupling_calls=0

### BigCodeBench/618 (bigcodebench)
  statement: Generate and visualize a Pandas DataFrame of the results of football matches for multiple teams 'Team' with random goals 'Goals' and penalties 'Penalty Cost'. Penalties are converted into fines according to penalty costs. The function should output with:     pd.DataFrame: A da...
  features: stmt_len_log=6.55 code_len_log=6.86 ast_nodes_log=3.40 num_functions=1 comp_steps=0.0 coupling_imports=4 coupling_calls=0

### BigCodeBench/760 (bigcodebench)
  statement: Creates a random DataFrame with 100 records. Each record consists of an ID (ranging from 1 to 100), Name (randomly selected from provided lists of Latin and other names), Date of Birth (randomly generated dates between the specified years), and Email (constructed using the nam...
  features: stmt_len_log=7.50 code_len_log=8.15 ast_nodes_log=3.69 num_functions=1 comp_steps=0.0 coupling_imports=5 coupling_calls=0

### BigCodeBench/765 (bigcodebench)
  statement: Process files from a dictionary by checking if the file exists, and if it has content, then copies it to a target directory. The function should output with:     copied_files (list): A list of full file paths that were copied. You should write self-contained code starting with...
  features: stmt_len_log=5.96 code_len_log=6.81 ast_nodes_log=2.71 num_functions=1 comp_steps=1.0 coupling_imports=3 coupling_calls=0

### BigCodeBench/870 (bigcodebench)
  statement: Calculate the mean of numerical values in each position across tuples in a list. Non-numeric values are ignored, and means are computed only from available data. That means that missing data in some of the tuples is simply ignored. A DataFrame with one columns named 'Mean Valu...
  features: stmt_len_log=6.95 code_len_log=7.31 ast_nodes_log=3.69 num_functions=1 comp_steps=1.0 coupling_imports=3 coupling_calls=0

### BigCodeBench/917 (bigcodebench)
  statement: Forecasts the share closing prices for the next 7 days using the ARIMA model and plots the forecast. The function should output with:     Tuple[List[float], Axes]: A tuple containing:     A list with forecasted prices for the next 7 days.     A matplotlib Axes object containin...
  features: stmt_len_log=6.35 code_len_log=7.15 ast_nodes_log=3.58 num_functions=1 comp_steps=2.0 coupling_imports=5 coupling_calls=0

### HumanEval/101 (humaneval)
  statement: You will be given a string of words separated by commas or spaces. Your task is     to split the string into words and return an array of the words.          For example:     words_string("Hi, my name is John") == ["Hi", "my", "name", "is", "John"]     words_string("One, two, ...
  features: stmt_len_log=5.86 code_len_log=5.98 ast_nodes_log=1.95 num_functions=1 comp_steps=0.0 coupling_imports=0 coupling_calls=0

### HumanEval/102 (humaneval)
  statement: This function takes two positive numbers x and y and returns the     biggest even integer number that is in the range [x, y] inclusive. If      there's no such number, then the function should return -1.      For example:     choose_num(12, 15) = 14     choose_num(13, 12) = -1
  features: stmt_len_log=5.63 code_len_log=5.76 ast_nodes_log=2.08 num_functions=1 comp_steps=1.0 coupling_imports=0 coupling_calls=0

### HumanEval/116 (humaneval)
  statement: In this Kata, you have to sort an array of non-negative integers according to     number of ones in their binary representation in ascending order.     For similar number of ones, sort based on decimal value.      It must be implemented like this:     >>> sort_array([1, 5, 2, ...
  features: stmt_len_log=6.04 code_len_log=6.14 ast_nodes_log=1.95 num_functions=1 comp_steps=0.0 coupling_imports=0 coupling_calls=0

### HumanEval/129 (humaneval)
  statement: Given a grid with N rows and N columns (N >= 2) and a positive integer k,      each cell of the grid contains a value. Every integer in the range [1, N * N]     inclusive appears exactly once on the cells of the grid.      You have to find the minimum path of length k in the g...
  features: stmt_len_log=7.18 code_len_log=7.22 ast_nodes_log=2.08 num_functions=1 comp_steps=1.0 coupling_imports=1 coupling_calls=0

### HumanEval/154 (humaneval)
  statement: You are given 2 words. You need to return True if the second word or any of its rotations is a substring in the first word     cycpattern_check("abcd","abd") => False     cycpattern_check("hello","ell") => True     cycpattern_check("whassup","psus") => False     cycpattern_che...
  features: stmt_len_log=5.98 code_len_log=6.09 ast_nodes_log=2.08 num_functions=1 comp_steps=1.0 coupling_imports=0 coupling_calls=0

### HumanEval/159 (humaneval)
  statement: You're a hungry rabbit, and you already have eaten a certain number of carrots,     but now you need to eat more carrots to complete the day's meals.     you should return an array of [ total number of eaten carrots after your meals,                                     the num...
  features: stmt_len_log=6.84 code_len_log=6.90 ast_nodes_log=2.20 num_functions=1 comp_steps=0.0 coupling_imports=0 coupling_calls=0

### HumanEval/32 (humaneval)
  statement: Evaluates polynomial with coefficients xs at point x.     return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
  features: stmt_len_log=4.75 code_len_log=6.63 ast_nodes_log=3.93 num_functions=2 comp_steps=0.0 coupling_imports=1 coupling_calls=3

### HumanEval/65 (humaneval)
  statement: Circular shift the digits of the integer x, shift the digits right by shift     and return the result as a string.     If shift > number of digits, return digits reversed.     >>> circular_shift(12, 1)     "21"     >>> circular_shift(12, 2)     "12"
  features: stmt_len_log=5.52 code_len_log=5.69 ast_nodes_log=2.08 num_functions=1 comp_steps=0.0 coupling_imports=0 coupling_calls=0

### HumanEval/76 (humaneval)
  statement: Your task is to write a function that returns true if a number x is a simple     power of n and false in other cases.     x is a simple power of n if n**int=x     For example:     is_simple_power(1, 4) => true     is_simple_power(2, 2) => true     is_simple_power(8, 2) => true...
  features: stmt_len_log=5.95 code_len_log=6.06 ast_nodes_log=2.08 num_functions=1 comp_steps=0.0 coupling_imports=0 coupling_calls=0

### HumanEval/89 (humaneval)
  statement: Create a function encrypt that takes a string as an argument and     returns a string encrypted with the alphabet being rotated.      The alphabet should be rotated in a manner such that the letters      shift down by two multiplied to two places.     For example:     encrypt(...
  features: stmt_len_log=6.00 code_len_log=6.08 ast_nodes_log=1.95 num_functions=1 comp_steps=0.0 coupling_imports=0 coupling_calls=0

