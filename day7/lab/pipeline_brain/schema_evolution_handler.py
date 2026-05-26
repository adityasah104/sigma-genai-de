from typing import Dict, List, Tuple, Union
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType, BooleanType

def detect_schema_drift(expected_schema: Dict[str, str], actual_schema: Dict[str, str]) -> Dict[str, Union[Dict[str, str], List[Tuple[str, str]], str]]:
    new_columns = {k: v for k, v in actual_schema.items() if k not in expected_schema}
    removed_columns = {k: v for k, v in expected_schema.items() if k not in actual_schema}
    type_changes = {k: (expected_schema[k], actual_schema[k]) for k in expected_schema if expected_schema[k]!= actual_schema[k]}
    drift_severity = 'NONE'
    if new_columns:
        if any('null' not in v for v in new_columns.values()):
            drift_severity = 'HIGH'
        else:
            drift_severity = 'LOW'
    if removed_columns:
        drift_severity = 'BREAKING'
    return {
        'new_columns': new_columns,
       'removed_columns': removed_columns,
        'type_changes': type_changes,
        'drift_severity': drift_severity
    }

def decide_action(drift_report: Dict[str, Union[Dict[str, str], List[Tuple[str, str]], str]]) -> Dict[str, Dict[str, Union[str, int]]]:
    decisions = {}
    for column, dtype in drift_report['new_columns'].items():
        if dtype.endswith(' nullable'):
            decisions[column] = {'action': 'ADD_TO_SCHEMA','reason': 'New nullable column', 'risk_level': 0}
        elif dtype == 'float':
            decisions[column] = {'action': 'FLAG_ANOMALY','reason': 'New float column', 'risk_level': 2}
        else:
            decisions[column] = {'action': 'ADD_TO_SCHEMA','reason': 'New column', 'risk_level': 0}
    for column, (old_type, new_type) in drift_report['type_changes'].items():
        if '->' in new_type:
            old_type, new_type = new_type.split('->')
            if old_type == 'int' and new_type == 'float':
                decisions[column] = {'action': 'ADD_TO_SCHEMA','reason': 'Type widening', 'risk_level': 1}
            elif old_type == 'float' and new_type == 'int':
                decisions[column] = {'action': 'FLAG_ANOMALY','reason': 'Type narrowing', 'risk_level': 2}
    for column in drift_report['removed_columns']:
        decisions[column] = {'action': 'HALT','reason': 'Removed column', 'risk_level': 3}
    return decisions

def apply_schema_evolution(spark_df: DataFrame, decisions: Dict[str, Dict[str, Union[str, int]]], updated_schema: Dict[str, str]) -> Tuple[DataFrame, List[str]]:
    migration_notes = []
    for column, decision in decisions.items():
        if decision['action'] == 'DROP_SILENTLY':
            spark_df = spark_df.drop(column)
        elif decision['action'] == 'FLAG_ANOMALY':
            spark_df = spark_df.withColumn(f'{column}_anomaly', spark_df[column].isNull().cast('boolean'))
            migration_notes.append(f'Column {column} flagged for anomaly due to {decision["reason"]}')
        elif decision['action'] == 'ADD_TO_SCHEMA':
            migration_notes.append(f'Column {column} added with {decision["reason"]}')
    return spark_df, migration_notes

def handle_drift(expected_schema: Dict[str, str], actual_schema: Dict[str, str], spark_df: DataFrame = None) -> Dict[str, Union[Dict, List, str]]:
    drift_report = detect_schema_drift(expected_schema, actual_schema)
    decisions = decide_action(drift_report)
    evolution_report = {'drift_report': drift_report, 'decisions': decisions}
    if spark_df is not None:
        spark_df, migration_notes = apply_schema_evolution(spark_df, decisions, actual_schema)
        evolution_report['evolved_df'] = spark_df
        evolution_report['migration_notes'] = migration_notes
    print("Drift Report:", drift_report)
    print("Decisions:", decisions)
    return evolution_report
