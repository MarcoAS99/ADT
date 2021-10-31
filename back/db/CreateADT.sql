CREATE DATABASE IF NOT EXISTS ADT;
CREATE TABLE IF NOT EXISTS User(
    id INT AUTO_INCREMENT,
    nombre VARCHAR(50) ,
    email VARCHAR(50),
    tlf INT,
    paymethod VARCHAR(50),
    pwd VARCHAR(50) NOT NULL,
    privilege INT,
    PRIMARY KEY(id)
);
CREATE TABLE IF NOT EXISTS Taxi(
    id INT AUTO_INCREMENT,
    estado VARCHAR(8),
    ubicacion VARCHAR(100),
    destino VARCHAR(100),
    PRIMARY KEY(id),
);
CREATE TABLE IF NOT EXISTS Solicitud(
    id INT AUTO_INCREMENT,
    id_user INT,
    id_taxi INT,
    origen VARCHAR(50),
    destino VARCHAR(50),
    datenow DATETIME,
    estado VARCHAR(8),
    PRIMARY KEY(id),
    FOREIGN KEY(id_user) REFERENCES User(id),
    FOREIGN KEY(id_taxi) REFERENCES Taxi(id)
);