#! /usr/bin/env python3

import pandas as pd
import sys

def clean_airlinedata(file_path):
    '''Function to clean airline data from


    http://stat-computing.org/dataexpo/2009/the-data.html
    '''

    pdf0 = pd.read_csv(path, usecols = [0,1,2,3,4,5,6,7,8,9,11,12,14,15,16,17,18,21,23])
    pdf = pdf0.dropna()

    X_continuous = pdf[['Year', 'DayofMonth', 'DepTime', 'CRSDepTime', 'ArrTime', 'CRSArrTime',
                        'ActualElapsedTime', 'CRSElapsedTime', 'DepDelay', 'Distance']]
    X_dummies = pd.get_dummies(pdf, columns = ['Month', 'UniqueCarrier', 'Origin', 'Dest'])
    Y = pdf['ArrDelay']>0 # # FIXME: 'Cancelled' 'Diverted' could be used for multilevel logistic

    out_pdf = pd.concat([Y, X_continuous, X_dummies], 1)

    return out_pdf

def insert_partition_id_pdf(data_pdf, partition_num, partition_method):
    '''Insert arbitrary index to Pandas DataFrame for partition

    '''

    nrow = data_pdf.shape[0]

    if partition_method == "systematic":
        partition_id = pd.RangeIndex(nrow)
        out = pd.concat([pd.DataFrame(partition_id, columns='partition_id'), data_pdf], 1)

    return out


def insert_partition_id_sdf(data_sdf, partition_num, partition_method):
    ''''Insert arbitrary index to Spark DataFrame for partition

    assign a row ID and a partition ID using Spark SQL
    FIXME: WARN WindowExec: No Partition Defined for Window operation! Moving all data to a
    single partition, this can cause serious performance
    degradation. https://databricks.com/blog/2015/07/15/introducing-window-functions-in-spark-sql.html

    '''
    data_sdf.createOrReplaceTempView("data_sdf")
    data_sdf = spark.sql("""
    select *, row_id%20 as partition_id
    from (
    select *, row_number() over (order by rand()) as row_id
    from data_sdf
    )
    """)


    return data_sdf