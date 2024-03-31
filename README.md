# ACIT 3855 Microservices Project

test

## Team Members

- [x] 1. Nazira Fakhrurradi

## Project Description

This project consists of multiple microservices that work together as one whole system. The system receives requests for deliveries and delivery schedules. The request data will be stored in the database and the system will return a response to the user.

## Microservices

1. [x] Receiver Service
2. [x] Storage Service
3. [x] Scheduler/Processor Service
4. [x] Audit Service

## Receiver Service

The Receiver Service is responsible for receiving requests from the user and storing the request data in the database. The service will also return a response to the user.

## Storage Service

The Storage Service is responsible for storing the request data in the database.

## Scheduler/Processor Service

The Scheduler/Processor Service is responsible for processing the request data and schedule a process to the storage service GET endpoints every few seconds.

## Database

The database used for this project started off as a simple SQLITE local storage file. Then it was migrated to a MySQL database using the official docker image. Then, the MySQL database was changed from the local docker container to a cloud-based docker container using the official MySQL docker image. For me, I used Azure VM with Docker installed to run the MySQL container.

# [Go to top](#acit-3855-microservices-project)
