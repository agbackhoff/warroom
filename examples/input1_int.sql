{{ config(materialized='ephemeral', access = 'protected') }}

with

safecast as (
    select * from {{ ref('stg_src_aecorsoft_cdc_sap__acdoca') }}
),

rownumber AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY primary_key ORDER BY recordstamp DESC) AS rn
    FROM safecast
    {% if is_incremental() %}
        WHERE recordstamp > (SELECT MAX(recordstamp) FROM {{ this }})
    {% endif %}
),

final AS (
    SELECT *
    FROM rownumber
    WHERE rn = 1
)

SELECT * FROM final