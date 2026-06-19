import pandas as pd
import matplotlib.pyplot as plt

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

print("-" * 20 + " GENERATING BAR CHART " + "-" * 20)

# sort dataframe by top 10 books of all time
top_10 = jf.sort_values(by='TotalAllTime', ascending=False).head(10)

# set our index for easy display in the plot
# we'll also isolate just the year_column, because that's all we need to compare for
top_10 = top_10.set_index('Title')[year_columns]

# create a horizontally grouped bar chart
ax = top_10.plot(kind='barh', figsize=(14, 8), width=0.8, cmap='viridis')

# set up the chart information
plt.title('Top 10 Most Checked Out Books (Yearly Breakdown)', fontsize=16, fontweight='bold', pad=15)
plt.xlabel('Number of Checkouts', fontsize=12)
plt.ylabel('Book Title', fontsize=12)
plt.legend(title='Checkout Year', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()

# invert y-axis to show the most checked out at the top
plt.gca().invert_yaxis()

# save the graph
plt.savefig('most_checked_out_books.png', bbox_inches='tight')
print("-" * 20 + " GENERATED BAR CHART " + "-" * 20)

########################## Start Pie Chart ###################################
print("-" * 20 + " GENERATING PIE CHART " + "-" * 20)
# sf = subject frame
sf = cf.copy()
# remove the csv in Subjects
sf['Subjects'] = sf['Subjects'].str.split(',')

# make each subject it's own column
# ssf = split subject frame
ssf = sf.explode('Subjects')
ssf['Subjects'] = ssf['Subjects'].str.strip()
ssf = ssf[ssf['Subjects'] != '']

# get Total Checkout Numbers for each Subject
subject_totals = ssf.groupby('Subjects')['Checkouts'].sum().sort_values(ascending=False)

# separate the top 10 subjects from the rest to keep the chart readable
top_10_subjects = subject_totals.head(10)
other_subjects = subject_totals.iloc[10:].sum()

other = pd.Series([other_subjects], index=['Other'])

# Combine top 10 + Other back into one clean plotting series
# pf = pie frame (Combined data series for plotting)
pf = pd.concat([top_10_subjects, other])

# Clear bar chart from plt
plt.figure(figsize=(12, 10))

# setup pie chart
plt.pie(
    pf,
    labels=pf.index,
    autopct='%1.1f%%',
    startangle=140,
    colors=plt.cm.tab20.colors,
    textprops={'fontsize': 11}
)

plt.title('Subject Contribution to Total Checkout Volume', fontsize=16, fontweight='bold', pad=20)
# Forces the chart to be a perfect circle
plt.axis('equal')
plt.tight_layout()

plt.savefig('most_checked_out_subjects_pie.png', bbox_inches='tight')

print("-" * 20 + " GENERATED PIE CHART " + "-" * 20)
