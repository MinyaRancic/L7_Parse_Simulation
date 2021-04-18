# How to run

To change the input file, you'll have to modify which file it reads in on line `150`. Currently uses `payload.http`, which is a randomly generated file, created using `input_gen.py`.

Also inclued is `empircal.http`, which is some simple empirical HTTP data.

## Dependencies 
 I believe everything comes with base python, but it uses the following packages 
 - `itertools`
 - `re` (Regular expressions)
 - `functools`  

You will also need to use `python3` - I use version `3.5.2`, so it definitely will work on that
