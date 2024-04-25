CREATE DATABASE sistemaDeEvaluacionCodigo;
USE sistemaDeEvaluacionCodigo;

CREATE TABLE alumnos (
    idAlumno INT NOT NULL AUTO_INCREMENT, 
    nombreCompleto VARCHAR (40) NOT NULL,
    matricula VARCHAR (10) NOT NULL, 
    PRIMARY KEY (idAlumno)
    );
CREATE TABLE usuarios (
    idRegistro  INT NOT NULL AUTO_INCREMENT,
    usuario VARCHAR (20) NOT NULL,
    contrasenia VARBINARY (64) NOT NULL,
    FOREIGN KEY (idRegistro) REFERENCES alumnos(idAlumno)
);

