import test
import os 


  # — GAPS (Nucleus parity) — CRM CE participants ——————————
  - name: fact_union_meeting_bnp_participants_crm_ce
    layer: beta
    sub_layer: trusted
    engine: spark
    write_mode: overwrite
    overwrite_scope: partitions
    table_name: fact_union_bnp_ptcpt
    metadata: { domain: crm_plus }
    spark_config:
      executor_memory: "8g"
      driver_memory: "6g"
      shuffle_partitions: 32
      additional_configs: { spark.sql.ansi.enabled: "false", spark.task.maxDirectResultSize: "134217728", spark.driver.maxResultSize: "4g" }
    transform:
      sql_file: sql/crm_ce/fact_union_meeting_bnp_participants.sql
      iceberg_properties: { format-version: "3" }
      iceberg_partition_by: [interaction_type, interaction_source]
      sources:
        - { table: polaris.beta.trusted.crm_ce.fact_bnpp_ptcpt_crm_ce, alias: fact_bnpp_ptcpt }
        - { table: polaris.beta.trusted.crm_ce.fact_meeting_crm_ce, alias: fact_meeting }
        - { table: polaris.alpha.crm_nas.crm_plus_dim_date_bronze, alias: dim_date }

  - name: fact_union_event_bnp_participants_crm_ce
    layer: beta
    sub_layer: trusted
    engine: spark
    write_mode: overwrite
    overwrite_scope: partitions
    table_name: fact_union_bnp_ptcpt
    metadata: { domain: crm_plus }
    spark_config:
      executor_memory: "8g"
      driver_memory: "6g"
      shuffle_partitions: 32
      additional_configs: { spark.sql.ansi.enabled: "false", spark.task.maxDirectResultSize: "134217728", spark.driver.maxResultSize: "4g" }
    transform:
      sql_file: sql/crm_ce/fact_union_event_bnp_participants.sql
      iceberg_properties: { format-version: "3" }
      iceberg_partition_by: [interaction_type, interaction_source]
      sources:
        - { table: polaris.beta.trusted.crm_ce.fact_sub_event_attendees_crm_ce, alias: fact_sub_event_attendees }
        - { table: polaris.beta.trusted.crm_ce.dim_sub_event_crm_ce, alias: dim_sub_event }
        - { table: polaris.beta.trusted.crm_plus.dim_emp_info, alias: dim_emp_info }
        - { table: polaris.beta.trusted.crm_plus.dim_contact_info, alias: dim_contact_info }
        - { table: polaris.alpha.crm_nas.crm_plus_dim_date_bronze, alias: dim_date }

  - name: fact_union_meeting_contact_participants_crm_ce
    layer: beta
    sub_layer: trusted
    engine: spark
    write_mode: overwrite
    overwrite_scope: partitions
    table_name: fact_union_client_ptcpt
    metadata: { domain: crm_plus }
    spark_config:
      executor_memory: "8g"
      driver_memory: "6g"
      shuffle_partitions: 32
      additional_configs: { spark.sql.ansi.enabled: "false", spark.task.maxDirectResultSize: "134217728", spark.driver.maxResultSize: "4g" }
    transform:
      sql_file: sql/crm_ce/fact_union_meeting_contact_participants.sql
      iceberg_properties: { format-version: "3" }
      iceberg_partition_by: [interaction_type, interaction_source]
      sources:
        - { table: polaris.beta.trusted.crm_ce.fact_client_ptcpt_crm_ce, alias: fact_client_ptcpt }
        - { table: polaris.beta.trusted.crm_ce.fact_meeting_crm_ce, alias: fact_meeting }
        - { table: polaris.beta.trusted.crm_plus.dim_contact_info, alias: dim_contact_info }
        - { table: polaris.alpha.crm_nas.crm_plus_dim_date_bronze, alias: dim_date }

  - name: fact_union_event_contact_participants_crm_ce
    layer: beta
    sub_layer: trusted
    engine: spark
    write_mode: overwrite
    overwrite_scope: partitions
    table_name: fact_union_client_ptcpt
    metadata: { domain: crm_plus }
    spark_config:
      executor_memory: "8g"
      driver_memory: "6g"
      shuffle_partitions: 32
      additional_configs: { spark.sql.ansi.enabled: "false", spark.task.maxDirectResultSize: "134217728", spark.driver.maxResultSize: "4g" }
    transform:
      sql_file: sql/crm_ce/fact_union_event_contact_participants.sql
      iceberg_properties: { format-version: "3" }
      iceberg_partition_by: [interaction_type, interaction_source]
      sources:
        - { table: polaris.beta.trusted.crm_ce.fact_sub_event_attendees_crm_ce, alias: fact_sub_event_attendees }
        - { table: polaris.beta.trusted.crm_ce.dim_sub_event_crm_ce, alias: dim_sub_event }
        - { table: polaris.beta.trusted.crm_plus.dim_contact_info, alias: dim_contact_info }
        - { table: polaris.alpha.crm_nas.crm_plus_dim_date_bronze, alias: dim_date }
