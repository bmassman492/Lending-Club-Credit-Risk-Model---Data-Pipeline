with source as (
    select * from {{ source('raw', 'RAW_FRED_DATA') }}
),

deduped as (
    select
        date_trunc('month', "DATE"::date) as date,
        UNRATE::float                     as unemployment_rate,
        GDP::float                        as gdp,
        FEDFUNDS::float                   as federal_funds_rate,
        CPIAUCSL::float                   as consumer_price_index,
        MORTGAGE30US::float               as fixed_mortgage_rate,
        PSAVERT::float                    as personal_savings_rate
    from source
    qualify row_number() over (
        partition by date_trunc('month', "DATE"::date)
        order by "DATE"::date desc
    ) = 1
)

select * from deduped
