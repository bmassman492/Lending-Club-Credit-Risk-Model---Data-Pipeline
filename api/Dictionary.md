# API I/O Dictionary

## Inputs

The /predict request takes a JSON string with the below format. Included are real values from a record in training data for example format.
```bash
{
  "LOAN_AMOUNT": 15000.0,
  "LOAN_TERM_MONTHS": 36,
  "LOAN_INTEREST_RATE": 26.30,
  "LOAN_PURPOSE_IS_DEBT_CONSOLIDATION": 1,
  "LOAN_EMP_LENGTH": 9,
  "LOAN_OWNS_HOME": 0,
  "LOAN_ANNUAL_INCOME": 75000,
  "LOAN_APPLYING_AS_INDIVIDUAL": 1,
  "LOAN_DTI": 12.93,
  "LOAN_FICO_RANGE_LOW": 665.0,
  "LOAN_EARLIEST_CR_LINE": 2001,
  "LOAN_OPEN_ACC": 7,
  "LOAN_DELINQ_2YRS": 2.0,
  "LOAN_INQ_LAST_6MTHS": 1.0,
  "LOAN_TOT_HI_CRED_LIM": 44592.0,
  "LOAN_TOTAL_BC_LIMIT": 22300.0,
  "LOAN_MORT_ACC": 0.0,
  "LOAN_BC_UTIL": 67.4,
  "GDP": 19692.595,
  "FEDERAL_FUNDS_RATE": 1.16,
  "FIXED_MORTGAGE_RATE": 3.94,
  "PERSONAL_SAVINGS_RATE": 6.1,
  "LOAN_PRIOR_DELINQUENCY": 1,
  "LOAN_PRIOR_RECORD": 0
}
```

LOAN_AMOUNT: The dollar amount the borrower is requesting as a loan.

LOAN_TERM_MONTHS: The length of the loan term in months.

LOAN_INTEREST_RATE: The yearly interest rate on the loan.

LOAN_PURPOSE_IS_DEBT_CONSOLIDATION: 1 If the borrower is taking a loan to help pay off other debt. 0 if the borrower is taking a loan for any other reason.

LOAN_EMP_LENGTH: The number of years, out of the previous 10 years, that the borrower has been employed. 

LOAN_OWNS_HOME: 1 if the borrower has complete ownership of their home. 0 otherwise.

LOAN_ANNUAL_INCOME: The annual income of the borrower.

LOAN_APPLYING_AS_INDIVIDUAL: 1 if the borrower is applying as an individual, 0 if applying jointly.

LOAN_DTI: The Debt-To-Income Ratio of the loan. Calculated as the Monthly Payment divided by the borrower's Monthly Income, excluding mortgage and the requested loan. 

LOAN_FICO_RANGE_LOW: The lower boundary of the borrower's FICO credit score estimate. Exact credit score can be input here if known. 

LOAN_EARLIEST_CR_LINE: The year the borrower's first reported credit line was opened.

LOAN_OPEN_ACC: The number of open credit lines in the borrower's credit file.

LOAN_DELINQ_2YRS: The number of 30+ day past-due delinquencies the borrower has had in the past 2 years.

LOAN_INQ_LAST_6MTHS: The number of credit inquiries the borrower has made in the past 6 months.

LOAN_TOT_HI_CRED_LIM: The total credit limit across all of the borrower's accounts.

LOAN_TOTAL_BC_LIMIT: The borrower's total bankcard credit limit. 

LOAN_MORT_ACC: The number of mortgage accounts belonging to the borrower. 

LOAN_BC_UTIL: The Bankcard Utilization Rate. The borrower's total bankcard balance divided by total bankcard credit limit. 

GDP: The U.S. Gross Domestic Product in billions of dollars, from the quarter the loan begins. 

FEDERAL_FUNDS_RATE: The U.S. Federal Funds Rate from the month the loan begins.

FIXED_MORTGAGE_RATE: The U.S. Average 30-year fixed mortgage rate from the month the loan begins.

PERSONAL_SAVINGS_RATE: The U.S. Personal Savings Rate as a percentage of disposable income, from the month the loan begins.

LOAN_PRIOR_DELINQUENCY: 1 if the borrower has had a past credit delinquency, otherwise 0.

LOAN_PRIOR_RECORD: 1 if the borrower has had a past public record, such as bankruptcy. Otherwise, 0. 

## Outputs

The /predict request responds with a JSON string in the following format:
```bash
{
  "decision": "Deny",
  "charge_off_probability": 0.757,
  "threshold": 0.6
}
```
Where charge_off_probability is the predicted likelihood the borrower will charge off the loan, threshold is the hardcoded threshold of accepted probability for chargeoffs, and decision states "Approve" for probabilities below the threshold, and "Deny" for probabilities above it. 

