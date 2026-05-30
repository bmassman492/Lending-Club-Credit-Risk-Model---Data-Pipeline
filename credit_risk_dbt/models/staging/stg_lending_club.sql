with source as (
    select * from {{ source('raw', 'RAW_LC_DATA') }}
),

renamed as (
    select
        "id"                                                           as loan_id,
        "loan_status"                                                  as loan_status,
        to_date("issue_d", 'MON-YYYY')                                 as loan_issue_date,
        "loan_amnt"::float                                             as loan_amount,
        trim("term")                                                   as loan_term,
        try_to_double(replace("int_rate"::varchar, '%', ''))           as loan_interest_rate,
        "installment"::float                                           as loan_installment,
        "purpose"                                                      as loan_purpose,
        "emp_length"                                                   as loan_emp_length,
        "home_ownership"                                               as loan_home_ownership,
        "annual_inc"::float                                            as loan_annual_income,
        "application_type"                                             as loan_application_type,
        "addr_state"                                                   as loan_addr_state,
        "dti"::float                                                   as loan_dti,
        "fico_range_low"::float                                        as loan_fico_range_low,
        "fico_range_high"::float                                       as loan_fico_range_high,
        "earliest_cr_line"                                             as loan_earliest_cr_line,
        "open_acc"::int                                                as loan_open_acc,
        "total_acc"::int                                               as loan_total_acc,
        "revol_bal"::float                                             as loan_revol_bal,
        try_to_double(replace("revol_util"::varchar, '%', ''))         as loan_revol_util,
        "total_rev_hi_lim"::float                                      as loan_total_rev_hi_lim,
        "delinq_2yrs"::int                                             as loan_delinq_2yrs,
        "mths_since_last_delinq"::float                                as loan_mths_since_last_delinq,
        "mths_since_last_record"::float                                as loan_mths_since_last_record,
        "pub_rec"::int                                                 as loan_pub_rec,
        "pub_rec_bankruptcies"::int                                    as loan_pub_rec_bankruptcies,
        "acc_now_delinq"::int                                          as loan_acc_now_delinq,
        "tax_liens"::int                                               as loan_tax_liens,
        "inq_last_6mths"::int                                          as loan_inq_last_6mths,
        "tot_cur_bal"::float                                           as loan_tot_cur_bal,
        "tot_coll_amt"::float                                          as loan_tot_coll_amt,
        "tot_hi_cred_lim"::float                                       as loan_tot_hi_cred_lim,
        "total_bal_ex_mort"::float                                     as loan_total_bal_ex_mort,
        "total_bc_limit"::float                                        as loan_total_bc_limit,
        "avg_cur_bal"::float                                           as loan_avg_cur_bal,
        "mort_acc"::int                                                as loan_mort_acc,
        "bc_util"::float                                               as loan_bc_util,
        "bc_open_to_buy"::float                                        as loan_bc_open_to_buy,
        "percent_bc_gt_75"::float                                      as loan_percent_bc_gt_75,
        "num_accts_ever_120_pd"::int                                   as loan_num_accts_ever_120_pd,
        "pct_tl_nvr_dlq"::float                                        as loan_pct_tl_nvr_dlq
    from source
    where "issue_d" is not null
      and "loan_amnt" is not null
)

select * from renamed
