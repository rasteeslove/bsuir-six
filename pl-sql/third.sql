-- alter session set "_ORACLE_SCRIPT"=true;

-- 1: to code a procedure which accepts two names - schema1 and
-- schema2 - which represent the names for two schemas. the
-- procedure is then to return a list of tables present in the first
-- schema but not in the second, as well as a list of tables
-- which have the same name whose structure differs in the schemas.
-- the 1st list of tables to be sorted in an appropriate order
-- for them to be added to the second schema. if there are cyclic
-- dependencies, this info to be returned too.
-- use-case: dev and prod schemas

create user rdev identified by dev_pass;
create user rprod identified by prod_pass;

grant all privileges to rdev;
grant all privileges to rprod;

-- populating rdev:

create table rdev.Company (
    id number constraint CompanyPk primary key,
    name varchar2(30),
    email varchar2(30)
);

create table rdev.Employee (
    id number constraint EmployeePk primary key,
    first_name varchar2(30),
    last_name varchar2(30),
    is_manager number(1),
    company_id number references rdev.Company(id)
);

create table rdev.PersonalData (
    id number constraint PersonalDataPk primary key,
    birth_date date,
    salary number,
    employee_id number references rdev.Employee(id),
    constraint EmployeeConstraint unique (employee_id)
);

create table rdev.Bank (
    id number constraint BankPk primary key,
    name varchar2(30),
    email varchar2(30)
);

create table rdev.CompanyBank (
    company_id number not null,
    bank_id number not null,
    foreign key (company_id) references rdev.Company(id),
    foreign key (bank_id) references rdev.Bank(id),
    unique (company_id, bank_id)
);

-- populating rprod:

create table rprod.Company (
    id number constraint CompanyPk primary key,
    name varchar2(30),
    email varchar2(30)
);

create table rprod.Employee (
    id number constraint EmployeePk primary key,
    first_name varchar2(30),
    last_name varchar2(30),
    is_manager number(1),
    is_admin number(1),
    company_id number references rprod.Company(id)
);

create table rprod.Bank (
    id number constraint BankPk primary key,
    name varchar2(30),
    email varchar2(30)
);

create table rprod.CompanyBank (
    company_id number not null,
    bank_id number not null,
    foreign key (company_id) references rprod.Company(id),
    foreign key (bank_id) references rprod.Bank(id),
    unique (company_id, bank_id)
);

-- the procedure:

create or replace procedure rdiff(
    schema1 varchar2(20),
    schema2 varchar2(20)
) as
begin
    -- ...
end;

-- test the procedure:
-- ...


-- 2: to expand the procedure to also support procedures, functions,
-- and indexes

-- ...


-- 3: to add ddl update script generation, also aimed at deleting
-- objects present in the target schema but absent in the source schema

-- ...
