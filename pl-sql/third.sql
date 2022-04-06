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
-- ...

-- populating rprod:
-- ...

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
