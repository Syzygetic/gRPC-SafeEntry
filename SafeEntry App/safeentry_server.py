# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC SafeEntry server."""

from concurrent import futures
import logging

import grpc
#TODO: import _pb2 and _pb2_grpc
import safeentry_pb2
import safeentry_pb2_grpc

import pandas as pd
import numpy as np
import datetime
# Import SparkSession
from pyspark.sql import SparkSession

class Safeentry(safeentry_pb2_grpc.SafeentryServicer):

    def Register(self, request, context):
      # Read existing data from parquet file into a dataframe
      existingDataDF = pd.read_parquet(
        r'parquetFiles/userParticulars.parquet')
      # Create dataframe for new data to be added to the existing parquet file
      newDataDF = pd.DataFrame({"NRIC": [request.nric], "Name": [request.name]})
      # Combine existing data and new data dataframes into a dataframe
      updatedDataDF = pd.concat([existingDataDF, newDataDF], ignore_index=True)

      # Save updated data to parquet file
      updatedDataDF.to_parquet(
        r'parquetFiles/userParticulars.parquet')

      return safeentry_pb2.RegisterReply(registerresponse='Registration for %s (%s) successful.'
                                                         % (request.name, request.nric))

    def Login(self, request, context):
      # Create SparkSession
      spark = SparkSession.builder \
        .master("local[1]") \
        .appName("SparkByExamples.com") \
        .getOrCreate()

      parquetFile = spark.read.parquet(
        r'parquetFiles/userParticulars.parquet')
      parquetFile.createOrReplaceTempView("parquetFileView")
      loggedinUserNameQuery = spark.sql("SELECT Name FROM parquetFileView WHERE NRIC='{}'".format(request.nric))
      isEmptyResult = loggedinUserNameQuery.isEmpty()
      if isEmptyResult:
        return safeentry_pb2.LoginReply(loginresponse='NRIC %s not registered, please register to login.'
                                                         % (request.nric))
      else:
        loggedinUserName = loggedinUserNameQuery.collect()[0][0]
        return safeentry_pb2.LoginReply(loginresponse='Successfully logged in as %s (%s)'
                                                         % (loggedinUserName, request.nric), loginusername=loggedinUserName)

    def MOHLogin(self, request, context):
      # Create SparkSession
      spark = SparkSession.builder \
        .master("local[1]") \
        .appName("SparkByExamples.com") \
        .getOrCreate()

      parquetFile = spark.read.parquet(
        r'parquetFiles/mohOfficersLogin.parquet')
      parquetFile.createOrReplaceTempView("parquetFileView")
      mohOfficerLoginQuery = spark.sql("SELECT * FROM parquetFileView WHERE ID='{0}' AND Password='{1}'"
                                       .format(request.id, request.password))
      isEmptyResult = mohOfficerLoginQuery.isEmpty()
      if isEmptyResult:
        return safeentry_pb2.MOHLoginReply(mohloginresponse='Invalid login attempt, please try another login combination.')
      else:
        return safeentry_pb2.MOHLoginReply(mohloginresponse='Successfully logged in to MOH special access system.'
                                        , loginstatus="Logged in")

    def DeclareCovidCase(self, request, context):
      # Read existing data from parquet file into a dataframe
      existingDataDF = pd.read_parquet(
        r'parquetFiles/covidLocation.parquet')
      # Create dataframe for new data to be added to the existing parquet file
      newDataDF = pd.DataFrame({"Location": [request.location], "Date": [request.date], "Time": [request.time]})
      # Combine existing data and new data dataframes into a dataframe
      updatedDataDF = pd.concat([existingDataDF, newDataDF], ignore_index=True)

      # Save updated data to parquet file
      updatedDataDF.to_parquet(
        r'parquetFiles/covidLocation.parquet')

      return safeentry_pb2.DeclareCovidCaseReply(declarecovidcaseresponse='Declaration for new covid case location at %s on %s, %s successful.'
                                                         % (request.location, request.date, request.time))

    def CheckIn(self, request, context):
      # Read existing data from parquet file into a dataframe
      existingDataDF = pd.read_parquet(
        r'parquetFiles/userLocationHist.parquet')
      # Create dataframe for new data to be added to the existing parquet file
      newDataDF = pd.DataFrame(
        {"NRIC": [request.nric], "Date": [request.date], "Time": [request.time], "Location": [request.location],
         "Status": ['Check-in']})
      # Combine existing data and new data dataframes into a dataframe
      updatedDataDF = pd.concat([existingDataDF, newDataDF], ignore_index=True)

      # Save updated data to parquet file
      updatedDataDF.to_parquet(
        r'parquetFiles/userLocationHist.parquet')

      return safeentry_pb2.CheckInReply(
        checkinresponse='Hello %s (%s), you have successfully checked-in to %s on %s at %s.'
                        % (request.name, request.nric, request.location, request.date, request.time))

    def CheckOut(self, request, context):
      # Read existing data from parquet file into a dataframe
      existingDataDF = pd.read_parquet(
        r'parquetFiles/userLocationHist.parquet')
      # Create dataframe for new data to be added to the existing parquet file
      newDataDF = pd.DataFrame(
        {"NRIC": [request.nric], "Date": [request.date], "Time": [request.time], "Location": [request.location],
         "Status": ['Check-out']})
      # Combine existing data and new data dataframes into a dataframe
      updatedDataDF = pd.concat([existingDataDF, newDataDF], ignore_index=True)

      # Save updated data to parquet file
      updatedDataDF.to_parquet(
        r'parquetFiles/userLocationHist.parquet')

      return safeentry_pb2.CheckOutReply(
        checkoutresponse='Hello %s (%s), you have successfully checked-out from %s on %s at %s.'
                        % (request.name, request.nric, request.location, request.date, request.time))

    def CheckInFamily(self, request_iterator, context):
      for request in request_iterator:
        # Read existing data from parquet file into a dataframe
        existingDataDF = pd.read_parquet(
          r'parquetFiles/userLocationHist.parquet')
        # Create dataframe for new data to be added to the existing parquet file
        newDataDF = pd.DataFrame(
          {"NRIC": [request.nric], "Date": [request.date], "Time": [request.time], "Location": [request.location],
           "Status": ['Check-in']})
        # Combine existing data and new data dataframes into a dataframe
        updatedDataDF = pd.concat([existingDataDF, newDataDF], ignore_index=True)

        # Save updated data to parquet file
        updatedDataDF.to_parquet(
          r'parquetFiles/userLocationHist.parquet')

      return safeentry_pb2.CheckInFamilyReply(
        checkinfamilyresponse='Hello %s (%s), you have successfully checked-in with your family members to %s on %s at %s.'
                        % (request.name, request.nric, request.location, request.date, request.time))

    def CheckOutFamily(self, request_iterator, context):
      for request in request_iterator:
        # Read existing data from parquet file into a dataframe
        existingDataDF = pd.read_parquet(
          r'parquetFiles/userLocationHist.parquet')
        # Create dataframe for new data to be added to the existing parquet file
        newDataDF = pd.DataFrame(
          {"NRIC": [request.nric], "Date": [request.date], "Time": [request.time], "Location": [request.location],
           "Status": ['Check-out']})
        # Combine existing data and new data dataframes into a dataframe
        updatedDataDF = pd.concat([existingDataDF, newDataDF], ignore_index=True)

        # Save updated data to parquet file
        updatedDataDF.to_parquet(
          r'parquetFiles/userLocationHist.parquet')

      return safeentry_pb2.CheckOutFamilyReply(
        checkoutfamilyresponse='Hello %s (%s), you have successfully checked-out with your family members from %s on %s at %s.'
                        % (request.name, request.nric, request.location, request.date, request.time))

    def ListLocationsHistory(self, request, context):
      # Create SparkSession
      spark = SparkSession.builder \
        .master("local[1]") \
        .appName("SparkByExamples.com") \
        .getOrCreate()

      parquetFile = spark.read.parquet(
        r'parquetFiles/userLocationHist.parquet')
      parquetFile.createOrReplaceTempView("parquetFileView")
      userLocationsQuery = spark.sql("SELECT Date, Time, Location, Status FROM parquetFileView WHERE NRIC='{}'".format(request.nric))
      isEmptyResult = userLocationsQuery.isEmpty()
      if isEmptyResult:
        yield safeentry_pb2.ListLocationsHistoryReply(listlocationshistoryresponse='No Existing Location History. '
                                                                                    'You have yet checked-in or checked-out from any location.')
      else:
        ListLocationsHistoryArray = np.array(userLocationsQuery.select('Date', 'Time', 'Location', 'Status').collect())

        yield safeentry_pb2.ListLocationsHistoryReply(
          listlocationshistoryresponse= '\nFollowing are your Location History:')

        for i in range(len(ListLocationsHistoryArray)):
          yield safeentry_pb2.ListLocationsHistoryReply(
          listlocationshistoryresponse= '%d) %s %s %s %s'
                                        % (i + 1, ListLocationsHistoryArray[i][0], ListLocationsHistoryArray[i][1],
                                           ListLocationsHistoryArray[i][2], ListLocationsHistoryArray[i][3]))

    def CheckCovidExposure(self, request, context):
      # datetime object containing current date and time
      past14days = datetime.datetime.utcnow() + datetime.timedelta(hours=+8) + datetime.timedelta(days=-14)

      # dd/mm/YY H:M:S
      date_string = past14days.strftime("%Y-%m-%d")
      time_string = past14days.strftime("%H:%M:%S")

      # Create SparkSession
      spark = SparkSession.builder \
        .master("local[1]") \
        .appName("SparkByExamples.com") \
        .getOrCreate()

      parquetFile = spark.read.parquet(
        r'parquetFiles/covidLocation.parquet')
      parquetFile.createOrReplaceTempView("parquetFileView")
      covidLocationsQuery = spark.sql(
        "SELECT Location, Date, Time FROM parquetFileView WHERE (CAST(Date AS date) > CAST('{0}' AS date)) "
        "OR ((CAST(Date AS date) = CAST('{0}' AS date)) AND (CAST(Time AS timestamp) >= CAST('{1}' AS timestamp)))"
        .format(date_string, time_string))
      if covidLocationsQuery.isEmpty():
        yield safeentry_pb2.CheckCovidExposureReply(checkcovidexposureresponse='No Existing Covid Exposure. ')
      else:
        CovidLocationsArray = np.array(covidLocationsQuery.select('Location', 'Date', 'Time').collect())

        count = 0

        for i in range(len(CovidLocationsArray)):

          parquetFile = spark.read.parquet(
            r'parquetFiles/userLocationHist.parquet')
          parquetFile.createOrReplaceTempView("parquetFileView")
          userCovidLocationsQuery = spark.sql(
            "SELECT p1.Location, p1.Date, p1.Time AS CheckinTime, p2.Time AS CheckoutTime "
            "FROM parquetFileView p1, parquetFileView p2 "
            "WHERE ((p1.NRIC='{0}' AND p1.Date='{1}' AND p1.Location='{2}' AND p1.Status='Check-in') "
            "AND (p2.NRIC='{0}' AND p2.Date='{1}' AND p2.Location='{2}' AND p2.Status='Check-out')) "
            "AND ((CAST(p1.Time AS timestamp) <= CAST('{3}' AS timestamp)) AND (CAST(p2.Time AS timestamp) >= CAST('{3}' AS timestamp)))"
              .format(request.nric, CovidLocationsArray[i][1], CovidLocationsArray[i][0], CovidLocationsArray[i][2]))
          if userCovidLocationsQuery.isEmpty():
            continue
          else:
            if count == 0:
              yield safeentry_pb2.CheckCovidExposureReply(
                checkcovidexposureresponse='\nPotential covid exposure at following locations:')
              yield safeentry_pb2.CheckCovidExposureReply(
                checkcovidexposureresponse='   Location    Date    CheckinTime  CheckoutTime')

            UserCovidLocationsArray = np.array(
              userCovidLocationsQuery.select('Location', 'Date', 'CheckinTime', 'CheckoutTime').collect()).tolist()

            yield safeentry_pb2.CheckCovidExposureReply(
              checkcovidexposureresponse='%d) %s %s %s %s'
                                         % (count + 1, UserCovidLocationsArray[0][0],
                                            UserCovidLocationsArray[0][1], UserCovidLocationsArray[0][2],
                                            UserCovidLocationsArray[0][3]))

            count += 1

        if count == 0:
          yield safeentry_pb2.CheckCovidExposureReply(checkcovidexposureresponse='No Existing Covid Exposure.')
        else:
          yield safeentry_pb2.CheckCovidExposureReply(checkcovidexposureresponse='You are required to monitor your '
                                                                                 'health for 14 days from the latest '
                                                                                 'exposure date!')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    safeentry_pb2_grpc.add_SafeentryServicer_to_server(Safeentry(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
