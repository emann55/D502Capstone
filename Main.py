import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Load csv file
df = pd.read_csv('CheckoutData.csv')

# Clean data
# Convert data types from Checkouts, and CheckoutYear
# Dropping incomplete records from Title, CheckoutYear, Checkouts, and Subjects
# cf = Clean Frame (with incomplete data removed)
cf = df
cf['Checkouts'] = pd.to_numeric(cf['Checkouts'], errors='coerce')
cf['CheckoutYear'] = pd.to_numeric(cf['CheckoutYear'], errors='coerce')
cf = cf.dropna(subset=['Title', 'CheckoutYear', 'Checkouts', 'Subjects'])

# Create a pivot table
# Index on the title, create columns for each unique value of CheckoutYear, with the values in those columns being set
# on the sum of Checkouts. Fill any without data for a particular year to 0 checkouts.
# cf_years = Clean Frame with Year data
cf_years = cf.pivot_table(
    index='Title',
    columns='CheckoutYear',
    values='Checkouts',
    aggfunc='sum',
    fill_value=0  # Fills years with 0 checkouts instead of leaving them as NaN
)

# We're done transforming the data, drop unneeded columns
# We no longer need
# CheckoutYear since it's split up into columns
# CheckoutMonth since it no longer provides useful information
# Checkouts since it's used to fill said columns
# UsageClass, CheckoutType, Publisher, since they won't be used for our analysis.
# xf = trimmed frame (Useless information for analysis removed)
xf = cf.drop(columns=['CheckoutYear', 'CheckoutMonth', 'Checkouts', 'UsageClass', 'CheckoutType', 'Publisher'])
# Sort alphabetically by Title
xf = xf.groupby('Title').first()

# Since both dataframes now use 'Title' as their index, we can cleanly join them together
# jf  = Joined Frame (Contains checked out year information)
jf = xf.join(cf_years).reset_index()

# Add an "All-Time Total" column at the very end
# cf_years will contain only the checkout year information, so summing it gives us our total checkout information
year_columns = cf_years.columns
jf['TotalAllTime'] = jf[year_columns].sum(axis=1)

# Print for Debugging
# Print total number of unique books
print(f"Total unique books in the dataset: {len(jf):,}\n")

# Print the first 10 rows
print("-" * 20 + " FIRST 10 UNIQUE BOOKS " + "-" * 20)
print(jf.head(10))
print("\n" + "-" * 70 + "\n")

# Print a random sample of 10 rows
print("-" * 20 + " RANDOM SAMPLE OF 10 UNIQUE BOOKS " + "-" * 20)
print(jf.sample(10))
print("-" * 75)