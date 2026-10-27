SELECT
     UIDS AS uids
    ,EMPLOYEE_NAME AS employeename
    ,M360TEAM AS m360team
    ,EMAIL AS employeeemail
    ,CONCAT_WS(',', COLLECT_SET(MANAGER)) AS manager
    ,CONCAT_WS(',', COLLECT_SET(MANAGER_UID)) AS manager_uid
    ,CONCAT_WS(',', COLLECT_SET(EXCO)) AS exco
    ,CONCAT_WS(',', COLLECT_SET(EXCO_UID)) AS excouid
    ,CONCAT_WS(',', COLLECT_SET(COALESCE(u1.NTLogin, r1.sam))) AS employee_ntlogin
    ,CONCAT_WS(',', COLLECT_SET(COALESCE(u2.NTLogin, r2.sam))) AS manager_ntlogin
    ,CONCAT_WS(',', COLLECT_SET(COALESCE(u3.NTLogin, r3.sam))) AS exco_ntlogin
    ,END_DATE AS date
    ,CASE
        WHEN END_DATE IS NULL THEN 'False'
        ELSE 'True'
     END AS is_leaver
    ,CASE
        WHEN M360_CORPORATE_SPONSOR = 'Y' THEN True
        ELSE False
     END AS is_m360_corporate_sponsor
FROM m360teams t
LEFT JOIN permissions_enhanced_refog r1 ON r1.uid = t.UIDS
LEFT JOIN permissions_user u1 ON u1.GlobalUID = t.UIDS
LEFT JOIN permissions_enhanced_refog r2 ON r2.uid = t.MANAGER_UID
LEFT JOIN permissions_user u2 ON u2.GlobalUID = t.MANAGER_UID
LEFT JOIN permissions_enhanced_refog r3 ON r3.uid = t.EXCO_UID
LEFT JOIN permissions_user u3 ON u3.GlobalUID = t.EXCO_UID
GROUP BY UIDS, EMPLOYEE_NAME, M360TEAM, EMAIL, END_DATE, M360_CORPORATE_SPONSOR




  # — GAPS (Nucleus parity) — m360 ————————————————
  - name: m360_ntlogin
    layer: beta
    sub_layer: trusted
    engine: spark
    write_mode: overwrite
    metadata: {domain: crm_plus}
    spark_config: {additional_configs: {spark.sql.ansi.enabled: "false"}}
    data_quality: {on_failure: fail, checks: [{type: row_count_min, value: 1}]}
    transform:
      sql_file: sql/crm_plus/m360_ntlogin.sql
      sources:
        - {table: polaris.alpha.qdi_apex.m360_researchers_referential, alias: m360teams}
        - {table: polaris.alpha.cia.permissions_enhanced_refog, alias: permissions_enhanced_refog}
        - {table: polaris.alpha.cia.permissions_user, alias: permissions_user}




