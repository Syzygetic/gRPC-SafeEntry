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
"""The Python implementation of the GRPC SafeEntry client."""

from __future__ import print_function

import logging

import grpc
#TODO: import _pb2 and _pb2_grpc
import safeentry_pb2
import safeentry_pb2_grpc
import datetime

# Simple user registration & login required before use of service
def regLogin():
  while loggedinUser == {} and mohLoginStatus == {}:
    print('''
    Welcome to SafeEntry.

    1) Login
    2) Register
    3) MOH Officers Login
    ''')

    userRegLoginChoice = input("Please enter the number beside desired feature to select it: ")

    if userRegLoginChoice == "1":
      # Simple log in with user's NRIC to simulate user logging in with SingPass
      userLoginNRIC = input("Please enter your NRIC to login with SingPass: ")
      runLogin(userLoginNRIC)
    elif userRegLoginChoice == "2":
      userNRIC = input("Please enter your NRIC: ")
      userName = input("Please enter your Name as per Identity Card: ")
      runRegister(userNRIC, userName)
    elif userRegLoginChoice == "3":
      mohLoginID = input("Please enter your Login ID: ")
      mohLoginPW = input("Please enter your Login Password: ")
      runMOHLogin(mohLoginID, mohLoginPW)
    else:
      print("Invalid option!")

# Run Register function
def runRegister(nric, name):
  # NOTE(gRPC Python Team): .close() is possible on a channel and should be
  # used in circumstances in which the with statement does not fit the needs
  # of the code.
  with grpc.insecure_channel('localhost:50051') as channel:
    # TODO: initiate the stub
    stub = safeentry_pb2_grpc.SafeentryStub(channel)
    response = stub.Register(safeentry_pb2.RegisterRequest(nric=nric, name=name))
    print("\n" + str(response.registerresponse))

# Run Login function
def runLogin(nric):
  with grpc.insecure_channel('localhost:50051') as channel:
    # TODO: initiate the stub
    stub = safeentry_pb2_grpc.SafeentryStub(channel)
    response = stub.Login(safeentry_pb2.LoginRequest(nric=nric))
    print("\n" + str(response.loginresponse))
    if response.loginusername != "":
      loggedinUser[nric] = response.loginusername

# Run MOH Officers Login function
def runMOHLogin(id, password):
  with grpc.insecure_channel('localhost:50051') as channel:
    # TODO: initiate the stub
    stub = safeentry_pb2_grpc.SafeentryStub(channel)
    response = stub.MOHLogin(safeentry_pb2.MOHLoginRequest(id=id, password=password))
    print("\n" + str(response.mohloginresponse))
    if response.loginstatus != "":
      mohLoginStatus[id] = response.loginstatus

# MOH special access function to declare a COVID-19 case location
def mohFunction():
  while mohLoginStatus != {}:
    print('''
    Special access function for MOH.

    1) Declare COVID-19 Case Locations
    2) Logout
    ''')

    mohOfficerOption = input("Please enter the number beside desired feature to select it: ")

    if mohOfficerOption == "1":
      covidLocation = input("Please enter the new COVID-19 case location: ")
      covidDate = input("Please enter the new COVID-19 case date (Format: yyyy-mm-dd, Eg: 2022-06-26): ")
      covidTime = input("Please enter the new COVID-19 case time (Format: hh/mm/ss, Eg: 20:50:07): ")
      runDeclareCovidCase(covidLocation, covidDate, covidTime)
    elif mohOfficerOption == "2":
      mohLoginStatus.clear()

      regLogin()

      if loggedinUser != {}:
        mainFunctions()
      elif mohLoginStatus != {}:
        mohFunction()
    else:
      print("Invalid option!")

# Run DeclareCovidCase function
def runDeclareCovidCase(location, date, time):
  with grpc.insecure_channel('localhost:50051') as channel:
    # TODO: initiate the stub
    stub = safeentry_pb2_grpc.SafeentryStub(channel)
    response = stub.DeclareCovidCase(safeentry_pb2.DeclareCovidCaseRequest(location=location, date=date, time=time))
    print(str(response.declarecovidcaseresponse))

# Enables logged in users to use the main functions offered by the SafeEntry service
def mainFunctions():
  loggedinUserName = list(loggedinUser.values())[0]
  loggedinUserNRIC = list(loggedinUser.keys())[0]

  runCheckCovidExposure(loggedinUserNRIC)

  while loggedinUser != {}:
    print('''
    Welcome to SafeEntry, %s (%s)
  
    1) Check-in
    2) Check-out
    3) Check-in for Family Members
    4) Check-out for Family Members
    5) List my Location History
    6) Check Covid Exposure
    7) Logout
    ''' % (loggedinUserName, loggedinUserNRIC))

    userOption = input("Please enter the number beside desired feature to select it: ")

    if userOption == "1":
      checkinLocation = input("Please enter your check-in location: ")
      useCurrentDateTime = input("Check-in with current date and time? (y/n): ")
      if useCurrentDateTime.lower() == "y":
        # datetime object containing current date and time
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=+8)

        # YY-mm-dd H:M:S
        date_string = now.strftime("%Y-%m-%d")
        time_string = now.strftime("%H:%M:%S")

        runCheckin(loggedinUserName, loggedinUserNRIC, checkinLocation, date_string, time_string)
      elif useCurrentDateTime.lower() == "n":
        checkinDate = input("Please enter your check-in date (Format: yyyy-mm-dd, Eg: 2022-06-26): ")
        checkinTime = input("Please enter your check-in time (Format: hh/mm/ss, Eg: 20:50:07): ")

        runCheckin(loggedinUserName, loggedinUserNRIC, checkinLocation, checkinDate, checkinTime)
    elif userOption == "2":
      checkoutLocation = input("Please enter your check-out location: ")
      useCurrentDateTime = input("Check-out with current date and time? (y/n): ")
      if useCurrentDateTime.lower() == "y":
        # datetime object containing current date and time
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=+8)

        # YY-mm-dd H:M:S
        date_string = now.strftime("%Y-%m-%d")
        time_string = now.strftime("%H:%M:%S")

        runCheckout(loggedinUserName, loggedinUserNRIC, checkoutLocation, date_string, time_string)
      elif useCurrentDateTime.lower() == "n":
        checkoutDate = input("Please enter your check-out date (Format: yyyy-mm-dd, Eg: 2022-06-26): ")
        checkoutTime = input("Please enter your check-out time (Format: hh/mm/ss, Eg: 20:50:07): ")

        runCheckout(loggedinUserName, loggedinUserNRIC, checkoutLocation, checkoutDate, checkoutTime)
    elif userOption == "3":
      checkinLocation = input("Please enter check-in location: ")
      useCurrentDateTime = input("Check-in with current date and time? (y/n): ")
      if useCurrentDateTime.lower() == "y":
        # datetime object containing current date and time
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=+8)

        # YY/mm/dd H:M:S
        checkinDate = now.strftime("%Y-%m-%d")
        checkinTime = now.strftime("%H:%M:%S")
      elif useCurrentDateTime.lower() == "n":
        checkinDate = input("Please enter your check-in date (Format: yyyy-mm-dd, Eg: 2022-06-26): ")
        checkinTime = input("Please enter your check-in time (Format: hh/mm/ss, Eg: 20:50:07): ")

      numOfFamilyMembers = int(input("Please indicate how many family members you're checking in for: "))
      runCheckinFamily(loggedinUserName, loggedinUserNRIC, checkinLocation, numOfFamilyMembers, checkinDate, checkinTime)
    elif userOption == "4":
      checkoutLocation = input("Please enter check-out location: ")
      useCurrentDateTime = input("Check-out with current date and time? (y/n): ")
      if useCurrentDateTime.lower() == "y":
        # datetime object containing current date and time
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=+8)

        # YY/mm/dd H:M:S
        checkoutDate = now.strftime("%Y-%m-%d")
        checkoutTime = now.strftime("%H:%M:%S")
      elif useCurrentDateTime.lower() == "n":
        checkoutDate = input("Please enter your check-out date (Format: yyyy-mm-dd, Eg: 2022-06-26): ")
        checkoutTime = input("Please enter your check-out time (Format: hh/mm/ss, Eg: 20:50:07): ")

      numOfFamilyMembers = int(input("Please indicate how many family members you're checking out for: "))
      runCheckoutFamily(loggedinUserName, loggedinUserNRIC, checkoutLocation, numOfFamilyMembers, checkoutDate, checkoutTime)
    elif userOption == "5":
      runListLocationsHistory(loggedinUserNRIC)
    elif userOption == "6":
      runCheckCovidExposure(loggedinUserNRIC)
    elif userOption == "7":
      loggedinUser.clear()

      regLogin()

      if loggedinUser != {}:
        mainFunctions()
      elif mohLoginStatus != {}:
        mohFunction()
    else:
      print("Invalid option!")

# Run Self Check-in function
def runCheckin(name, nric, location, date, time):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        #TODO: initiate the stub
        stub = safeentry_pb2_grpc.SafeentryStub(channel)
        response = stub.CheckIn(safeentry_pb2.CheckInRequest(name=name, nric=nric, location=location, date=date, time=time))
        print(str(response.checkinresponse))

# Run Self Check-out function
def runCheckout(name, nric, location, date, time):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        #TODO: initiate the stub
        stub = safeentry_pb2_grpc.SafeentryStub(channel)
        response = stub.CheckOut(safeentry_pb2.CheckOutRequest(name=name, nric=nric, location=location, date=date, time=time))
        print(str(response.checkoutresponse))

def checkinFamilyClientStreamRequest(userName, userNRIC, location, numOfFamMembs, date, time):
  checkinCount = -1
  # Checking in the Family Members with Client-side Streaming
  while checkinCount != numOfFamMembs:
    # For the convenience of the user, the user will be checked-in along with his family members automatically, as well.
    if checkinCount == -1:
      checkin_family_request = safeentry_pb2.CheckInFamilyRequest(name=userName, nric=userNRIC,
                                                                  location=location, date=date, time=time)
      yield checkin_family_request
    else:
      familyMemberNRIC = input("Please enter family member %s's NRIC: " % str(checkinCount + 1))
      familyMemberName = input("Please enter family member %s's Name: " % str(checkinCount + 1))

      checkin_family_request = safeentry_pb2.CheckInFamilyRequest(name=familyMemberName, nric=familyMemberNRIC,
                                                                  location=location, date=date, time=time)
      yield checkin_family_request

    checkinCount += 1

# Run Family Check-in function
def runCheckinFamily(userName, userNRIC, location, numOfFamMembs, date, time):
    with grpc.insecure_channel('localhost:50051') as channel:
        #TODO: initiate the stub
        stub = safeentry_pb2_grpc.SafeentryStub(channel)
        response = stub.CheckInFamily(checkinFamilyClientStreamRequest(userName, userNRIC, location, numOfFamMembs, date, time))
        print(str(response.checkinfamilyresponse))

def checkoutFamilyClientStreamRequest(userName, userNRIC, location, numOfFamMembs, date, time):
  checkoutCount = -1
  # Checking out the Family Members with Client-side Streaming
  while checkoutCount != numOfFamMembs:
    # For the convenience of the user, the user will be checked-out along with his family members automatically, as well.
    if checkoutCount == -1:
      checkout_family_request = safeentry_pb2.CheckOutFamilyRequest(name=userName, nric=userNRIC,
                                                                  location=location, date=date, time=time)
      yield checkout_family_request
    else:
      familyMemberNRIC = input("Please enter family member %s's NRIC: " % str(checkoutCount + 1))
      familyMemberName = input("Please enter family member %s's Name: " % str(checkoutCount + 1))

      checkout_family_request = safeentry_pb2.CheckOutFamilyRequest(name=familyMemberName, nric=familyMemberNRIC,
                                                                    location=location, date=date, time=time)
      yield checkout_family_request

    checkoutCount += 1

# Run Family Check-out function
def runCheckoutFamily(userName, userNRIC, location, numOfFamMembs, date, time):
    with grpc.insecure_channel('localhost:50051') as channel:
        #TODO: initiate the stub
        stub = safeentry_pb2_grpc.SafeentryStub(channel)
        response = stub.CheckOutFamily(checkoutFamilyClientStreamRequest(userName, userNRIC, location, numOfFamMembs, date, time))
        print(str(response.checkoutfamilyresponse))

# Run List my Location History function
def runListLocationsHistory(nric):
    with grpc.insecure_channel('localhost:50051') as channel:
      # TODO: initiate the stub
      stub = safeentry_pb2_grpc.SafeentryStub(channel)
      responses = stub.ListLocationsHistory(safeentry_pb2.ListLocationsHistoryRequest(nric=nric))

      for response in responses:
        print(str(response.listlocationshistoryresponse))

# Run Check Covid Exposure Notification function
def runCheckCovidExposure(nric):
    with grpc.insecure_channel('localhost:50051') as channel:
      # TODO: initiate the stub
      stub = safeentry_pb2_grpc.SafeentryStub(channel)
      responses = stub.CheckCovidExposure(safeentry_pb2.CheckCovidExposureRequest(nric=nric))

      for response in responses:
        print(str(response.checkcovidexposureresponse))

if __name__ == '__main__':
    loggedinUser = {}
    mohLoginStatus = {}

    logging.basicConfig()

    regLogin()

    if loggedinUser != {}:
      mainFunctions()
    elif mohLoginStatus != {}:
      mohFunction()


