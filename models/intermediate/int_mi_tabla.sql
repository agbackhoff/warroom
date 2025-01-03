{{ config(materialized='ephemeral') }}

with staging as (
    select * from {{ ref('stg_mi_tabla') }}
),

deduplicacion as (
    select
        *,
        row_number() over (
            partition by pk_mi_tabla
            order by recordstamp desc
        ) as rownum
    from staging
    {% if is_incremental() %}
        where recordstamp > (select max(recordstamp) from {{ this }})
    {% endif %}
),

final as (
    select
        *
    from deduplicacion
    where rownum = 1
)

select * from final