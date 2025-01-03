{{ config(materialized='ephemeral') }}

with source as (
    select *
    from {{ source('mi_source', 'mi_tabla') }}
),

staged as (
    select
        {{ dbt_utils.generate_surrogate_key(['id', 'created_at']) }} as pk_mi_tabla,
        SAFE_CAST(client AS STRING) AS client,
        SAFE_CAST(addrnumber AS STRING) AS addrnumber,
        SAFE_CAST(persnumber AS STRING) AS persnumber,
        SAFE_CAST(date_from AS DATE) AS date_from,
        SAFE_CAST(consnumber AS STRING) AS consnumber,
        SAFE_CAST(flgdefault AS STRING) AS flgdefault,
        SAFE_CAST(flg_nouse AS STRING) AS flg_nouse,
        SAFE_CAST(home_flag AS STRING) AS home_flag,
        SAFE_CAST(smtp_addr AS STRING) AS smtp_addr,
        SAFE_CAST(smtp_srch AS STRING) AS smtp_srch,
        SAFE_CAST(dft_receiv AS STRING) AS dft_receiv,
        SAFE_CAST(r3_user AS STRING) AS r3_user,
        SAFE_CAST(encode AS STRING) AS encode,
        SAFE_CAST(tnef AS STRING) AS tnef,
        SAFE_CAST(valid_from AS STRING) AS valid_from,
        SAFE_CAST(valid_to AS STRING) AS valid_to,
        SAFE_CAST(_dataaging AS DATE) AS _dataaging,
        SAFE_CAST(recordstamp AS TIMESTAMP) AS recordstamp
    from source
)

select * from staged
