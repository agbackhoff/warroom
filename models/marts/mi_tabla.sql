{{ config(materialized='table') }}

select * from {{ ref('int_mi_tabla') }}