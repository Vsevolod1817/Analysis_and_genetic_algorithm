This code implements a connection to the MySQL database (mydb),
then data is received from the database, 
the fitness function is determined, then the best sql query in terms of execution time is output using a genetic algorithm.
The visualization method, comparative analysis, and analysis do the best values were chosen as the method of analyzing the results.

Libraries that were used in the code:
1) mysql-connector-python (for connecting to the MySQL Workbench database)
2) pandas (for data processing and analysis) 
3) random (for generating random numbers)
4) matplotlib (for creating graphs)
5) deap (to implement a genetic algorithm
6) time (to measure query execution time)
7) tkinter (for creating a graphical interface)

To work, you need a MySQL database (mydb), the creation script and the model are added to the project.
MySQL Workbench version 8.0 is used to work with the database.